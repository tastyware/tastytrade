from __future__ import annotations

import asyncio
import json
from asyncio import Queue, QueueEmpty
from collections import defaultdict
from collections.abc import AsyncIterator, Coroutine, Generator
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from ssl import SSLContext, create_default_context
from types import TracebackType
from typing import Any, Callable, Optional, TypedDict, TypeVar, Union, cast

from pydantic import model_validator
from websockets.asyncio.client import ClientConnection, connect
from websockets.exceptions import ConnectionClosed

from tastytrade import logger, version_str
from tastytrade.account import Account, AccountBalance, CurrentPosition, TradingStatus
from tastytrade.dxfeed import (
    Candle,
    Greeks,
    Profile,
    Quote,
    Summary,
    TheoPrice,
    TimeAndSale,
    Trade,
    Underlying,
)
from tastytrade.order import (
    InstrumentType,
    OrderChain,
    PlacedComplexOrder,
    PlacedOrder,
)
from tastytrade.session import OAuthSession, Session
from tastytrade.utils import TastytradeData, TastytradeError, set_sign_for
from tastytrade.watchlists import Watchlist

CERT_STREAMER_URL = "wss://streamer.cert.tastyworks.com"
STREAMER_URL = "wss://streamer.tastyworks.com"

DXLINK_VERSION = "0.1-DXF-JS/0.3.0"


class QuoteAlert(TastytradeData):
    """
    Dataclass that contains information about a quote alert
    """

    user_external_id: str
    symbol: str
    alert_external_id: str
    expires_at: int
    completed_at: datetime
    created_at: datetime
    triggered_at: datetime
    field: str
    operator: str
    threshold: str
    threshold_numeric: Decimal
    dx_symbol: str


class ExternalTransaction(TastytradeData):
    """
    Dataclass containing information on an external transaction (eg money movement).
    """

    id: int
    account_number: str
    amount: Decimal
    bank_account_type: str
    banking_date: date
    created_at: datetime
    direction: str
    disbursement_type: str
    ext_transfer_id: str
    funds_available_date: date
    is_cancelable: bool
    is_clearing_accepted: bool
    state: str
    transfer_method: str
    updated_at: datetime


class UnderlyingYearGainSummary(TastytradeData):
    """
    Dataclass that contains information about the yearly gain
    or loss for an underlying
    """

    year: int
    account_number: str
    symbol: str
    instrument_type: InstrumentType
    fees: Decimal
    commissions: Decimal
    yearly_realized_gain: Decimal
    realized_lot_gain: Decimal

    @model_validator(mode="before")
    @classmethod
    def validate_price_effects(cls, data: Any) -> Any:
        return set_sign_for(
            data,
            [
                "fees",
                "commissions",
                "yearly_realized_gain",
                "realized_lot_gain",
            ],
        )


class SubscriptionType(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the subscription types
    for the alert streamer.
    """

    ACCOUNT = "connect"
    HEARTBEAT = "heartbeat"
    PUBLIC_WATCHLISTS = "public-watchlists-subscribe"
    QUOTE_ALERTS = "quote-alerts-subscribe"
    USER_MESSAGE = "user-message-subscribe"


#: List of all possible types to stream with the alert streamer
AlertType = Union[
    AccountBalance,
    ExternalTransaction,
    PlacedComplexOrder,
    PlacedOrder,
    OrderChain,
    CurrentPosition,
    QuoteAlert,
    TradingStatus,
    UnderlyingYearGainSummary,
    Watchlist,
]
T = TypeVar("T", bound=AlertType)
MAP_ALERTS: dict[str, type[AlertType]] = {
    "AccountBalance": AccountBalance,
    "ComplexOrder": PlacedComplexOrder,
    "ExternalTransaction": ExternalTransaction,
    "Order": PlacedOrder,
    "OrderChain": OrderChain,
    "CurrentPosition": CurrentPosition,
    "QuoteAlert": QuoteAlert,
    "TradingStatus": TradingStatus,
    "UnderlyingYearGainSummary": UnderlyingYearGainSummary,
    "PublicWatchlists": Watchlist,
}

#: List of all possible types to stream with the data streamer
EventType = Union[
    Candle,
    Greeks,
    Profile,
    Quote,
    Summary,
    TheoPrice,
    TimeAndSale,
    Trade,
    Underlying,
]
U = TypeVar("U", bound=EventType)
MAP_EVENTS: dict[str, type[EventType]] = {
    "Candle": Candle,
    "Greeks": Greeks,
    "Profile": Profile,
    "Quote": Quote,
    "Summary": Summary,
    "TheoPrice": TheoPrice,
    "TimeAndSale": TimeAndSale,
    "Trade": Trade,
    "Underlying": Underlying,
}
MAP_EVENTS_REVERSE = {v: k for k, v in MAP_EVENTS.items()}


async def _do_nothing(streamer: AlertStreamer | DXLinkStreamer) -> None:
    pass


class AlertStreamer:
    """
    Used to subscribe to account-level updates (balances, orders, positions),
    public watchlist updates, quote alerts, and user-level messages. It should
    always be initialized as an async context manager, or by awaiting it,
    since the object cannot be fully instantiated without async.

    Example usage::

        from tastytrade import Account, AlertStreamer
        from tastytrade.order import PlacedOrder

        async with AlertStreamer(session) as streamer:
            accounts = Account.get_accounts(session)

            # updates to balances, orders, and positions
            await streamer.subscribe_accounts(accounts)
            # changes in public watchlists
            await streamer.subscribe_public_watchlists()
            # quote alerts configured by the user
            await streamer.subscribe_quote_alerts()

            async for order in streamer.listen(PlacedOrder):
                print(order)

    Or::

        streamer = await AlertStreamer(session)

    """

    def __init__(
        self,
        session: Session,
        disconnect_args: tuple[Any, ...] = (),
        disconnect_fn: Callable[..., Coroutine[Any, Any, None]] = _do_nothing,
        reconnect_args: tuple[Any, ...] = (),
        reconnect_fn: Callable[..., Coroutine[Any, Any, None]] = _do_nothing,
    ):
        #: The active session used to initiate the streamer or make requests
        self.token: str = session.session_token
        if isinstance(session, OAuthSession):
            self.token = "Bearer " + self.token
        #: The base url for the streamer websocket
        self.base_url: str = CERT_STREAMER_URL if session.is_test else STREAMER_URL
        #: An async function to be called upon reconnection. The first argument must be
        #: of type `AlertStreamer` and will be a reference to the streamer object.
        self.reconnect_fn = reconnect_fn
        #: Variable number of arguments to pass to the reconnect function
        self.reconnect_args = reconnect_args
        #: An async function to be called upon disconnection. The first argument must be
        #: of type `AlertStreamer` and will be a reference to the streamer object.
        self.disconnect_fn = disconnect_fn
        #: Variable number of arguments to pass to the reconnect function
        self.disconnect_args = disconnect_args
        #: The proxy URL, if any, associated with the session
        self.proxy = session.proxy
        #: Counter used to track the request ID for the streamer
        self.request_id = 0

        self._queues: dict[str, Queue[AlertType]] = defaultdict(Queue)
        self._websocket: Optional[ClientConnection] = None
        self._connect_task = asyncio.create_task(self._connect())
        self._reconnect_task: Optional[asyncio.Task[None]] = None
        self._heartbeat_task: Optional[asyncio.Task[None]] = None
        self._closing = False
        self._tasks: set[asyncio.Task[Any]] = set()

    async def __aenter__(self) -> AlertStreamer:
        time_out = 100
        while not self._websocket:
            await asyncio.sleep(0.1)
            time_out -= 1
            if time_out < 0:
                raise TastytradeError("Connection timed out")

        return self

    def __await__(self) -> Generator[Any, None, AlertStreamer]:
        return self.__aenter__().__await__()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        """
        Closes the websocket connection and cancels the pending tasks.
        """
        if not self._closing:  # can only be called once
            self._closing = True
            self._connect_task.cancel()
            tasks = [self._connect_task]
            if self._heartbeat_task and not self._heartbeat_task.done():
                self._heartbeat_task.cancel()
                tasks.append(self._heartbeat_task)
            if self._reconnect_task and not self._reconnect_task.done():
                self._reconnect_task.cancel()
                tasks.append(self._reconnect_task)
            await asyncio.gather(*tasks)
            await self._websocket.wait_closed()  # type: ignore

    async def _connect(self) -> None:
        """
        Connect to the websocket server using the URL and authorization
        token provided during initialization.
        """
        reconnecting = False
        async for websocket in connect(self.base_url, proxy=self.proxy):
            self._websocket = websocket
            self._heartbeat_task = asyncio.create_task(self._heartbeat())
            logger.debug("Websocket connection established.")

            if reconnecting:
                self._reconnect_task = asyncio.create_task(
                    self.reconnect_fn(self, *self.reconnect_args)
                )
            try:
                async for raw_message in websocket:
                    logger.debug("raw message: %s", raw_message)
                    data = json.loads(raw_message)
                    type_str = data.get("type")
                    if type_str is not None:
                        await self._map_message(type_str, data["data"])
            except ConnectionClosed as e:
                logger.error(f"Websocket connection closed with {e}")
            except asyncio.CancelledError:
                logger.debug("Websocket interrupted, cancelling main loop.")
                return await self.close()
            finally:
                self._tasks.add(  # prevent garbage collection
                    asyncio.create_task(self.disconnect_fn(self, *self.disconnect_args))
                )
            logger.debug("Websocket connection closed, retrying...")
            reconnecting = True

    async def listen(self, alert_class: type[T]) -> AsyncIterator[T]:
        """
        Iterate over non-heartbeat messages received from the streamer,
        mapping them to their appropriate data class and yielding them.

        This is designed to be friendly for type checking; the return
        type will be the same class you pass in.

        :param alert_class:
            the type of alert to listen for, should be of :any:`AlertType`
        """
        cls_str = next(k for k, v in MAP_ALERTS.items() if v == alert_class)
        while True:
            item = await self._queues[cls_str].get()
            yield cast(T, item)

    async def _map_message(self, type_str: str, data: dict[str, Any]) -> None:
        """
        I'm not sure what the user-status messages look like, so they're absent.
        """
        if type_str not in MAP_ALERTS:
            logger.fatal(
                f"Unknown message type {type_str} received: {data}, please open an "
                f"issue!"
            )
        else:
            await self._queues[type_str].put(MAP_ALERTS[type_str](**data))  # type: ignore

    async def subscribe_accounts(self, accounts: list[Account]) -> None:
        """
        Subscribes to account-level updates (balances, orders, positions).

        :param accounts: list of :class:`Account` to subscribe to updates for
        """
        await self._subscribe(
            SubscriptionType.ACCOUNT, [a.account_number for a in accounts]
        )

    async def subscribe_public_watchlists(self) -> None:
        """
        Subscribes to public watchlist updates.
        """
        await self._subscribe(SubscriptionType.PUBLIC_WATCHLISTS)

    async def subscribe_quote_alerts(self) -> None:
        """
        Subscribes to quote alerts (which are configured at a user level).
        """
        await self._subscribe(SubscriptionType.QUOTE_ALERTS)

    async def subscribe_user_messages(self, session: Session) -> None:
        """
        Subscribes to user-level messages, e.g. new account creation.
        """
        await self._subscribe(
            SubscriptionType.USER_MESSAGE, value=session.user.external_id
        )

    async def _heartbeat(self) -> None:
        """
        Sends a heartbeat message every 15 seconds to keep the connection
        alive.
        """
        try:
            while True:
                # send the heartbeat every 15 seconds
                await asyncio.sleep(15)
                await self._subscribe(SubscriptionType.HEARTBEAT)
        except asyncio.CancelledError:
            logger.debug("Websocket interrupted, cancelling heartbeat.")
        except ConnectionClosed:  # if the message fires while reconnecting
            pass

    async def _subscribe(
        self,
        subscription: SubscriptionType,
        value: Union[str, list[str], None] = None,
    ) -> None:
        """
        Subscribes to a :class:`SubscriptionType`. Depending on the kind of
        subscription, the value parameter may be required.
        """
        self.request_id += 1
        message: dict[str, Any] = {
            "auth-token": self.token,
            "action": subscription.value,
            "request-id": self.request_id,
            "source": version_str,
        }
        if value:
            message["value"] = value
        logger.debug("sending alert subscription: %s", message)
        await self._websocket.send(json.dumps(message))  # type: ignore


class DXLinkStreamer:
    """
    A :class:`DXLinkStreamer` object is used to fetch quotes or greeks for a
    given symbol or list of symbols. It should always be initialized as an
    async context manager, or by awaiting it, since the object cannot be
    fully instantiated without async.

    Example usage::

        from tastytrade import DXLinkStreamer
        from tastytrade.dxfeed import Quote

        # must be a production session
        async with DXLinkStreamer(session) as streamer:
            subs = ['SPY']  # list of quotes to subscribe to
            await streamer.subscribe(Quote, subs)
            quote = await streamer.get_event(Quote)
            print(quote)

    Or::

        streamer = await DXLinkStreamer(session)

    """

    def __init__(
        self,
        session: Session,
        disconnect_args: tuple[Any, ...] = (),
        disconnect_fn: Callable[..., Coroutine[Any, Any, None]] = _do_nothing,
        reconnect_args: tuple[Any, ...] = (),
        reconnect_fn: Callable[..., Coroutine[Any, Any, None]] = _do_nothing,
        ssl_context: SSLContext = create_default_context(),
    ):
        self._queues: dict[str, Queue[EventType]] = defaultdict(Queue)
        self._channels: dict[str, int] = {
            "Candle": 1,
            "Greeks": 3,
            "Profile": 5,
            "Quote": 7,
            "Summary": 9,
            "TheoPrice": 11,
            "TimeAndSale": 13,
            "Trade": 15,
            "Underlying": 17,
        }
        self._subscription_state: dict[str, str] = defaultdict(lambda: "CHANNEL_CLOSED")
        #: An async function to be called upon reconnection. The first argument must be
        #: of type `DXLinkStreamer` and will be a reference to the streamer object.
        self.reconnect_fn = reconnect_fn
        #: Variable number of arguments to pass to the reconnect function
        self.reconnect_args = reconnect_args
        #: An async function to be called upon disconnection. The first argument must be
        #: of type `DXLinkStreamer` and will be a reference to the streamer object.
        self.disconnect_fn = disconnect_fn
        #: Variable number of arguments to pass to the disconnect function
        self.disconnect_args = disconnect_args
        #: The proxy URL, if any, associated with the session
        self.proxy = session.proxy

        self._authenticated = False
        self._wss_url = session.dxlink_url
        self._auth_token = session.streamer_token
        self._ssl_context = ssl_context
        self._disconnect_called = False
        self._heartbeat_task: Optional[asyncio.Task[None]] = None
        self._reconnect_task: Optional[asyncio.Task[None]] = None
        self._closing = False
        self._websocket: ClientConnection
        self._tasks: set[asyncio.Task[Any]] = set()

    async def __aenter__(self) -> DXLinkStreamer:
        self._connect_task = asyncio.create_task(self._connect())
        time_out = 100
        while not self._authenticated:
            await asyncio.sleep(0.1)
            time_out -= 1
            if time_out < 0:
                raise TastytradeError("Connection timed out")

        return self

    def __await__(self) -> Generator[Any, None, DXLinkStreamer]:
        return self.__aenter__().__await__()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        """
        Closes the websocket connection and cancels the heartbeat task.
        """
        if not self._closing:  # can only be called once
            self._closing = True
            self._connect_task.cancel()
            tasks = [self._connect_task]
            if self._heartbeat_task:
                self._heartbeat_task.cancel()
                tasks.append(self._heartbeat_task)
            if self._reconnect_task is not None and not self._reconnect_task.done():
                self._reconnect_task.cancel()
                tasks.append(self._reconnect_task)
            await asyncio.gather(*tasks)
            await self._websocket.wait_closed()

    async def _connect(self) -> None:
        """
        Connect to the websocket server using the URL and
        authorization token provided during initialization.
        """
        reconnecting = False

        class DXLinkMessage(TypedDict):
            channel: int
            data: list[Any]
            message: str
            state: str
            type: str

        async for websocket in connect(
            self._wss_url, ssl=self._ssl_context, proxy=self.proxy
        ):
            self._websocket = websocket
            await self._setup_connection()
            try:
                async for raw_message in websocket:
                    message = cast(DXLinkMessage, json.loads(raw_message))
                    logger.debug("received: %s", message)
                    if (
                        message["type"] == "FEED_DATA"
                    ):  # This is the most common message type
                        await self._map_message(message["data"])
                    elif message["type"] == "SETUP":
                        await self._authenticate_connection()
                    elif message["type"] == "AUTH_STATE":
                        if message["state"] == "AUTHORIZED":
                            logger.debug("Websocket connection established.")
                            self._authenticated = True
                            self._heartbeat_task = asyncio.create_task(
                                self._heartbeat()
                            )
                        # run reconnect hook upon auth completion
                        if reconnecting:
                            self._subscription_state.clear()
                            reconnecting = False
                            self._reconnect_task = asyncio.create_task(
                                self.reconnect_fn(self, *self.reconnect_args)
                            )
                    elif message["type"] == "CHANNEL_OPENED":
                        channel = next(
                            k
                            for k, v in self._channels.items()
                            if v == message["channel"]
                        )
                        self._subscription_state[channel] = "CHANNEL_OPENED"
                        logger.debug("Channel opened: %s", message)
                    elif message["type"] == "CHANNEL_CLOSED":
                        channel = next(
                            k
                            for k, v in self._channels.items()
                            if v == message["channel"]
                        )
                        del self._subscription_state[channel]
                        logger.debug("Channel closed: %s", message)
                    elif message["type"] == "FEED_CONFIG":
                        logger.debug("Feed configured: %s", message)
                    elif message["type"] == "KEEPALIVE":
                        pass
                    elif message["type"] == "ERROR":
                        logger.error(f"Fatal streamer error: {message['message']}")
                        return await self.close()
                    else:
                        logger.error(f"Unknown message: {message}")
            except ConnectionClosed as e:
                logger.error(f"Websocket connection closed with {e}")
                if e.rcvd and e.rcvd.code == 1009:
                    logger.error(
                        "Subscription message too long! Try reducing the number of "
                        "symbols."
                    )
                    return await self.close()
            except asyncio.CancelledError:
                logger.debug("Websocket interrupted, cancelling main loop.")
                return await self.close()
            finally:
                self._tasks.add(  # prevent garbage collection
                    asyncio.create_task(self.disconnect_fn(self, *self.disconnect_args))
                )
            logger.debug("Websocket connection closed, retrying...")
            reconnecting = True

    async def _setup_connection(self) -> None:
        message = {
            "type": "SETUP",
            "channel": 0,
            "keepaliveTimeout": 60,
            "acceptKeepaliveTimeout": 60,
            "version": DXLINK_VERSION,
        }
        await self._websocket.send(json.dumps(message))

    async def _authenticate_connection(self) -> None:
        message = {
            "type": "AUTH",
            "channel": 0,
            "token": self._auth_token,
        }
        await self._websocket.send(json.dumps(message))

    async def listen(self, event_class: type[U]) -> AsyncIterator[U]:
        """
        Using the existing subscriptions, pulls events of the given type and
        yield returns them. Never exits unless there's an error or the channel
        is closed.

        This is designed to be friendly for type checking; the return
        type will be the same class you pass in.

        :param event_class:
            the type of alert to listen for, should be of :any:`EventType`
        """
        while True:
            yield await self._queues[MAP_EVENTS_REVERSE[event_class]].get()  # type: ignore

    def get_event_nowait(self, event_class: type[U]) -> Optional[U]:
        """
        Using the existing subscriptions, pulls an event of the given type and
        returns it. If the queue is empty None is returned.

        This is designed to be friendly for type checking; the return
        type will be the same class you pass in.

        :param event_class:
            the type of alert to listen for, should be of :any:`EventType`
        """
        try:
            return self._queues[MAP_EVENTS_REVERSE[event_class]].get_nowait()  # type: ignore
        except QueueEmpty:
            return None

    async def get_event(self, event_class: type[U]) -> U:
        """
        Using the existing subscription, pulls an event of the given type and
        returns it.

        This is designed to be friendly for type checking; the return
        type will be the same class you pass in.

        :param event_class:
            the type of alert to listen for, should be of :any:`EventType`
        """
        return await self._queues[MAP_EVENTS_REVERSE[event_class]].get()  # type: ignore

    async def _heartbeat(self) -> None:
        """
        Sends a keepalive message every 30 seconds to keep the connection
        alive.
        """
        message = {"type": "KEEPALIVE", "channel": 0}
        try:
            while True:
                logger.debug("sending keepalive message: %s", message)
                await self._websocket.send(json.dumps(message))
                # send the heartbeat every 30 seconds
                await asyncio.sleep(30)
        except asyncio.CancelledError:
            logger.debug("Websocket interrupted, cancelling heartbeat.")
        except ConnectionClosed:  # if the message fires while reconnecting
            pass

    async def subscribe(
        self,
        event_class: type[EventType],
        symbols: list[str],
        refresh_interval: float = 0.1,
    ) -> None:
        """
        Subscribes to quotes for given list of symbols. Used for recurring data
        feeds.
        For candles, use :meth:`subscribe_candle` instead.

        :param event_class: type of subscription to add, should be of :any:`EventType`
        :param symbols: list of symbols to subscribe for
        :param refresh_interval:
            Time in seconds between fetching new events from dxfeed for this event type.
            You can try a higher value if processing quote updates quickly is not a high
            priority. Once refresh_interval is set for this event type and channel is
            opened, it cannot be changed later.
        """
        cls_str = MAP_EVENTS_REVERSE[event_class]
        if self._subscription_state[cls_str] != "CHANNEL_OPENED":
            await self._channel_request(cls_str, refresh_interval)
        message = {
            "type": "FEED_SUBSCRIPTION",
            "channel": self._channels[cls_str],
            "add": [{"symbol": symbol, "type": cls_str} for symbol in symbols],
        }
        logger.debug("sending subscription: %s", message)
        await self._websocket.send(json.dumps(message))

    async def unsubscribe_all(self, event_class: type[EventType]) -> None:
        """
        Unsubscribes to all events of the given event type.

        :param event_class: type of event to unsubscribe from.
        """
        message = {
            "type": "CHANNEL_CANCEL",
            "channel": self._channels[MAP_EVENTS_REVERSE[event_class]],
        }
        logger.debug("sending channel cancel: %s", message)
        await self._websocket.send(json.dumps(message))

    async def _channel_request(
        self, event_type: str, refresh_interval: float = 0.1
    ) -> None:
        message = {
            "type": "CHANNEL_REQUEST",
            "channel": self._channels[event_type],
            "service": "FEED",
            "parameters": {
                "contract": "AUTO",
            },
        }
        logger.debug("sending subscription: %s", message)
        await self._websocket.send(json.dumps(message))
        time_out = 100
        while self._subscription_state[event_type] != "CHANNEL_OPENED":
            await asyncio.sleep(0.1)
            time_out -= 1
            if time_out <= 0:
                raise TastytradeError("Subscription channel not opened")
        # setup the feed
        await self._channel_setup(event_type, refresh_interval)

    async def _channel_setup(
        self, event_type: str, refresh_interval: float = 0.1
    ) -> None:
        message: dict[str, Any] = {
            "type": "FEED_SETUP",
            "channel": self._channels[event_type],
            "acceptAggregationPeriod": refresh_interval,
            "acceptDataFormat": "COMPACT",
        }

        def dict_from_schema(event_class: Any) -> dict[str, list[Any]]:
            schema = event_class.schema()
            return {schema["title"]: list(schema["properties"].keys())}

        cls = MAP_EVENTS[event_type]
        accept = dict_from_schema(cls)
        message["acceptEventFields"] = accept
        # send message
        logger.debug("setting up feed: %s", message)
        await self._websocket.send(json.dumps(message))

    async def unsubscribe(
        self, event_class: type[EventType], symbols: list[str]
    ) -> None:
        """
        Removes existing subscription for given list of symbols.
        For candles, use :meth:`unsubscribe_candle` instead.

        :param event_class: type of subscription to remove
        :param symbols: list of symbols to unsubscribe from
        """
        if not self._authenticated:
            raise TastytradeError("Stream not authenticated")
        cls_str = MAP_EVENTS_REVERSE[event_class]
        message = {
            "type": "FEED_SUBSCRIPTION",
            "channel": self._channels[cls_str],
            "remove": [{"symbol": symbol, "type": cls_str} for symbol in symbols],
        }
        logger.debug("sending subscription: %s", message)
        await self._websocket.send(json.dumps(message))

    async def subscribe_candle(
        self,
        symbols: list[str],
        interval: str,
        start_time: datetime,
        extended_trading_hours: bool = False,
        refresh_interval: float = 0.1,
    ) -> None:
        """
        Subscribes to candle data for the given list of symbols.

        :param symbols: list of symbols to get data for
        :param interval:
            the width of each candle in time, e.g. '15s', '5m', '1h', '3d',
            '1w', '1mo'
        :param start_time: starting time for the data range
        :param extended_trading_hours: whether to include extended trading
        :param refresh_interval:
            Time in seconds between fetching new events from dxfeed for this event type.
            You can try a higher value if processing quote updates quickly is not a high
            priority. Once refresh_interval is set for this event type and channel is
            opened, it cannot be changed later.
        """
        cls_str = "Candle"
        if self._subscription_state[cls_str] != "CHANNEL_OPENED":
            await self._channel_request(cls_str, refresh_interval)
        ts = int(start_time.timestamp() * 1000)
        message = {
            "type": "FEED_SUBSCRIPTION",
            "channel": self._channels[cls_str],
            "add": [
                {
                    "symbol": (
                        f"{ticker}{{={interval}}}"
                        if extended_trading_hours
                        else f"{ticker}{{={interval},tho=true}}"
                    ),
                    "type": "Candle",
                    "fromTime": ts,
                }
                for ticker in symbols
            ],
        }
        await self._websocket.send(json.dumps(message))

    async def unsubscribe_candle(
        self,
        ticker: str,
        interval: Optional[str] = None,
        extended_trading_hours: bool = False,
    ) -> None:
        """
        Removes existing subscription for a candle.

        :param ticker: symbol to unsubscribe from
        :param interval: candle width to unsubscribe from
        :param extended_trading_hours:
            whether candle to unsubscribe from contains extended trading hours
        """
        message = {
            "type": "FEED_SUBSCRIPTION",
            "channel": self._channels["Candle"],
            "remove": [
                {
                    "symbol": (
                        f"{ticker}{{={interval}}}"
                        if extended_trading_hours
                        else f"{ticker}{{={interval},tho=true}}"
                    ),
                    "type": "Candle",
                }
            ],
        }
        await self._websocket.send(json.dumps(message))

    async def _map_message(self, message: list[Any]) -> None:
        """
        Takes the raw JSON data, parses the events and places them into their
        respective queues.

        :param message: raw JSON data from the websocket
        """
        logger.debug("received message: %s", message)
        if isinstance(message[0], str):
            msg_type = message[0]
        else:
            msg_type = message[0][0]
        data = message[1]
        # parse type or warn for unknown type
        if msg_type not in MAP_EVENTS:
            logger.fatal(
                f"Unknown message type {msg_type} received: {data}, please open an "
                f"issue!"
            )
        else:
            cls = MAP_EVENTS[msg_type]
            results = cls.from_stream(data)
            for r in results:
                await self._queues[msg_type].put(r)  # type: ignore
