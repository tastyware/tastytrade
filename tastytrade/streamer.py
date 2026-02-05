from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import AsyncIterator
from contextlib import AsyncExitStack, asynccontextmanager
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from ssl import SSLContext, create_default_context
from typing import Any, AsyncGenerator, Self, TypeAlias, TypedDict, TypeVar, cast

from anyio import (
    TASK_STATUS_IGNORED,
    AsyncContextManagerMixin,
    WouldBlock,
    create_memory_object_stream,
    create_task_group,
    fail_after,
)
from anyio import (
    Event as AnyioEvent,
)
from anyio.abc import TaskStatus
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from anyio.streams.stapled import StapledObjectStream
from httpx import AsyncClient
from httpx_ws import AsyncWebSocketSession, WebSocketDisconnect, aconnect_ws
from pydantic import model_validator

from tastytrade import logger, version_str
from tastytrade.account import Account, AccountBalance, CurrentPosition, TradingStatus
from tastytrade.dxfeed import (
    Candle,
    Event,
    Greeks,
    Profile,
    Quote,
    Summary,
    TheoPrice,
    TimeAndSale,
    Trade,
    Underlying,
)
from tastytrade.order import InstrumentType, PlacedComplexOrder, PlacedOrder
from tastytrade.session import Session
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


#: List of all possible types to stream with the alert streamer
AlertType: TypeAlias = (
    AccountBalance
    | ExternalTransaction
    | PlacedComplexOrder
    | PlacedOrder
    | CurrentPosition
    | QuoteAlert
    | TradingStatus
    | UnderlyingYearGainSummary
    | Watchlist
)
T = TypeVar("T", bound=AlertType)
MAP_ALERTS: dict[str, type[AlertType]] = {
    "AccountBalance": AccountBalance,
    "ComplexOrder": PlacedComplexOrder,
    "ExternalTransaction": ExternalTransaction,
    "Order": PlacedOrder,
    "CurrentPosition": CurrentPosition,
    "QuoteAlert": QuoteAlert,
    "TradingStatus": TradingStatus,
    "UnderlyingYearGainSummary": UnderlyingYearGainSummary,
    "PublicWatchlists": Watchlist,
}

#: List of all possible types to stream with the data streamer
U = TypeVar("U", bound=Event)
MAP_EVENTS: dict[str, type[Event]] = {
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


class AlertStreamer(AsyncContextManagerMixin):
    """
    Used to subscribe to account-level updates (balances, orders, positions),
    public watchlist updates, quote alerts, and user-level messages. It must
    always be initialized via its async context manager.

    Example usage::

        from tastytrade import Account, AlertStreamer
        from tastytrade.order import PlacedOrder

        async with AlertStreamer(session) as streamer:
            accounts = await Account.get(session)
            # updates to balances, orders, and positions
            await streamer.subscribe_accounts(accounts)
            # changes in public watchlists
            await streamer.subscribe_public_watchlists()
            # quote alerts configured by the user
            await streamer.subscribe_quote_alerts()

            async for order in streamer.listen(PlacedOrder):
                print(order)

    """

    _websocket: AsyncWebSocketSession

    def __init__(self, session: Session):
        self.session = session
        #: The base url for the streamer websocket
        self.base_url: str = CERT_STREAMER_URL if session.is_test else STREAMER_URL
        #: Counter used to track the request ID for the streamer
        self.request_id = 0
        self._queues: dict[str, StapledObjectStream[AlertType]] = defaultdict(
            lambda: StapledObjectStream(
                *create_memory_object_stream[AlertType](math.inf)
            )
        )

    @asynccontextmanager
    async def __asynccontextmanager__(self) -> AsyncGenerator[Self]:
        async with AsyncExitStack() as stack:
            if self.session.proxy:
                client = await stack.enter_async_context(
                    AsyncClient(proxy=self.session.proxy)
                )
            else:
                client = None
            self._websocket = await stack.enter_async_context(
                aconnect_ws(self.base_url, client=client)
            )
            logger.debug("Websocket connection established.")
            async with create_task_group() as tg:
                tg.start_soon(self._reader)
                yield self
                tg.cancel_scope.cancel()

    async def _reader(self) -> None:
        while True:
            data = await self._websocket.receive_json()
            logger.debug("received message: %s", data)
            type_str = data.get("type")
            if type_str is not None:
                await self._map_message(type_str, data["data"])

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
            item = await self._queues[cls_str].receive()
            yield cast(T, item)

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

    async def _subscribe(
        self,
        subscription: SubscriptionType,
        value: str | list[str] | None = None,
    ) -> None:
        """
        Subscribes to a :class:`SubscriptionType`. Depending on the kind of
        subscription, the value parameter may be required.
        """
        await self.session._refresh()
        self.request_id += 1
        message: dict[str, Any] = {
            "auth-token": f"Bearer {self.session.session_token}",
            "action": subscription.value,
            "request-id": self.request_id,
            "source": version_str,
        }
        if value:
            message["value"] = value
        logger.debug("sending alert subscription: %s", message)
        await self._websocket.send_json(message)

    async def _map_message(self, type_str: str, data: dict[str, Any]) -> None:
        # I'm not sure what the user status messages look like, so they're absent.
        if type_str not in MAP_ALERTS:
            logger.fatal(
                f"Unknown message type {type_str} received: {data}, please open an "
                f"issue!"
            )
        else:
            await self._queues[type_str].send(MAP_ALERTS[type_str](**data))


class DXLinkStreamer(AsyncContextManagerMixin):
    """
    A :class:`DXLinkStreamer` object is used to fetch quotes or greeks for a
    given symbol or list of symbols. It must always be initialized via its
    async context manager.

    Example usage::

        from tastytrade import DXLinkStreamer
        from tastytrade.dxfeed import Quote

        # must be a production session
        async with DXLinkStreamer(session) as streamer:
            subs = ['SPY']  # list of quotes to subscribe to
            await streamer.subscribe(Quote, subs)
            quote = await streamer.get_event(Quote)
            print(quote)

    """

    __slots__ = (
        "_auth_token",
        "_channels",
        "_channels_reversed",
        "_recv",
        "_send",
        "_ssl_context",
        "_subscription_state",
        "_websocket",
        "_wss_url",
        "session",
    )
    _websocket: AsyncWebSocketSession

    def __init__(
        self, session: Session, ssl_context: SSLContext = create_default_context()
    ):
        # initialize streams
        self._send: dict[str, MemoryObjectSendStream[Event]] = {}
        self._recv: dict[type[Event], MemoryObjectReceiveStream[Event]] = {}
        for name, event_cls in MAP_EVENTS.items():
            send, recv = create_memory_object_stream[event_cls](math.inf)  # type: ignore[valid-type]
            self._send[name] = send
            self._recv[event_cls] = recv
        self.session = session
        # channel mapping and subscription state
        self._channels: dict[str, int] = {
            k: i * 2 + 1 for i, k in enumerate(MAP_EVENTS)
        }
        self._channels_reversed: dict[int, str] = {
            v: k for k, v in self._channels.items()
        }
        # mapping of channel -> subscribed event
        self._subscription_state: dict[str, AnyioEvent] = {}
        # internal objects
        self._ssl_context = ssl_context

    @asynccontextmanager
    async def __asynccontextmanager__(self) -> AsyncGenerator[Self]:
        # Pull streamer tokens and urls
        data = await self.session._get("/api-quote-tokens")
        self._wss_url = data["dxlink-url"]
        self._auth_token = data["token"]
        async with AsyncClient(
            proxy=self.session.proxy, verify=self._ssl_context
        ) as client:
            try:
                async with aconnect_ws(self._wss_url, client=client) as self._websocket:
                    logger.debug("Websocket connection established.")
                    async with create_task_group() as tg:
                        await tg.start(self._reader)
                        yield self
                        tg.cancel_scope.cancel()
            except* WebSocketDisconnect as eg:
                if eg.subgroup(lambda e: getattr(e, "code", None) == 1009):
                    raise TastytradeError(
                        "Subscription message too long! Try reducing the number of "
                        "symbols."
                    ) from eg
                raise

    async def _reader(
        self, *, task_status: TaskStatus[None] = TASK_STATUS_IGNORED
    ) -> None:
        # connect to the websocket server using the URL and auth token

        class DXLinkMessage(TypedDict):
            channel: int
            data: list[Any]
            message: str
            state: str
            type: str

        await self._setup_connection()
        while True:
            message: DXLinkMessage = await self._websocket.receive_json()
            logger.debug("received: %s", message)
            if message["type"] == "FEED_DATA":
                await self._map_message(message["data"])
            elif message["type"] == "SETUP":
                await self._authenticate_connection()
            elif message["type"] == "AUTH_STATE":
                if message["state"] == "AUTHORIZED":
                    logger.debug("Websocket connection established.")
                    task_status.started()
            elif message["type"] == "CHANNEL_OPENED":
                key = self._channels_reversed[message["channel"]]
                self._subscription_state[key].set()
                logger.debug("Channel opened: %s", message)
            elif message["type"] == "CHANNEL_CLOSED":
                key = self._channels_reversed[message["channel"]]
                del self._subscription_state[key]
                logger.debug("Channel closed: %s", message)
            elif message["type"] == "FEED_CONFIG":
                logger.debug("Feed configured: %s", message)
            elif message["type"] == "KEEPALIVE":
                pass
            elif message["type"] == "ERROR":
                raise TastytradeError(f"Fatal streamer error: {message['message']}")
            else:
                logger.error(f"Unknown message: {message}")

    async def _setup_connection(self) -> None:
        message = {
            "type": "SETUP",
            "channel": 0,
            "keepaliveTimeout": 60,
            "acceptKeepaliveTimeout": 60,
            "version": DXLINK_VERSION,
        }
        await self._websocket.send_json(message)

    async def _authenticate_connection(self) -> None:
        message = {
            "type": "AUTH",
            "channel": 0,
            "token": self._auth_token,
        }
        await self._websocket.send_json(message)

    async def _map_message(self, message: list[Any]) -> None:
        # takes the JSON data, parses the events and places them into their queues
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
                self._send[msg_type].send_nowait(r)

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
        await self._websocket.send_json(message)
        with fail_after(10):
            await self._subscription_state[event_type].wait()
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
            schema = event_class.model_json_schema()
            return {schema["title"]: list(schema["properties"].keys())}

        cls = MAP_EVENTS[event_type]
        accept = dict_from_schema(cls)
        message["acceptEventFields"] = accept
        # send message
        logger.debug("setting up feed: %s", message)
        await self._websocket.send_json(message)

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
            yield await self._recv[event_class].receive()  # type: ignore[return-value, misc]

    def get_event_nowait(self, event_class: type[U]) -> U | None:
        """
        Using the existing subscriptions, pulls an event of the given type and
        returns it. If the queue is empty None is returned.

        This is designed to be friendly for type checking; the return
        type will be the same class you pass in.

        :param event_class:
            the type of alert to listen for, should be of :any:`EventType`
        """
        try:
            return self._recv[event_class].receive_nowait()  # type: ignore[return-value]
        except WouldBlock:
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
        return await self._recv[event_class].receive()  # type: ignore[return-value]

    async def subscribe(
        self,
        event_class: type[Event],
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
        cls_str = event_class.__name__
        if cls_str not in self._subscription_state:
            self._subscription_state[cls_str] = AnyioEvent()
            await self._channel_request(cls_str, refresh_interval)
        # always wait here to prevent race condition with multiple subscribes
        await self._subscription_state[cls_str].wait()
        message = {
            "type": "FEED_SUBSCRIPTION",
            "channel": self._channels[cls_str],
            "add": [{"symbol": symbol, "type": cls_str} for symbol in symbols],
        }
        logger.debug("sending subscription: %s", message)
        await self._websocket.send_json(message)

    async def unsubscribe_all(self, event_class: type[Event]) -> None:
        """
        Unsubscribes to all events of the given event type.

        :param event_class: type of event to unsubscribe from.
        """
        message = {
            "type": "CHANNEL_CANCEL",
            "channel": self._channels[event_class.__name__],
        }
        logger.debug("sending channel cancel: %s", message)
        await self._websocket.send_json(message)

    async def unsubscribe(self, event_class: type[Event], symbols: list[str]) -> None:
        """
        Removes existing subscription for given list of symbols.
        For candles, use :meth:`unsubscribe_candle` instead.

        :param event_class: type of subscription to remove
        :param symbols: list of symbols to unsubscribe from
        """
        cls_str = event_class.__name__
        message = {
            "type": "FEED_SUBSCRIPTION",
            "channel": self._channels[cls_str],
            "remove": [{"symbol": symbol, "type": cls_str} for symbol in symbols],
        }
        logger.debug("sending subscription: %s", message)
        await self._websocket.send_json(message)

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
        if cls_str not in self._subscription_state:
            self._subscription_state[cls_str] = AnyioEvent()
            await self._channel_request(cls_str, refresh_interval)
        # always wait here to prevent race condition with multiple subscribes
        await self._subscription_state[cls_str].wait()
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
                    "type": cls_str,
                    "fromTime": ts,
                }
                for ticker in symbols
            ],
        }
        await self._websocket.send_json(message)

    async def unsubscribe_candle(
        self,
        ticker: str,
        interval: str | None = None,
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
        await self._websocket.send_json(message)
