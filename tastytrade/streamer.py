import asyncio
import json
from asyncio import Lock, Queue
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from enum import Enum
from ssl import SSLContext, create_default_context
from typing import Any, AsyncIterator, Dict, List, Optional, Union

import websockets
from websockets import WebSocketClientProtocol

from tastytrade import logger
from tastytrade.account import (Account, AccountBalance, CurrentPosition,
                                TradingStatus)
from tastytrade.dxfeed import (Candle, Event, EventType, Greeks, Profile,
                               Quote, Summary, TheoPrice, TimeAndSale, Trade,
                               Underlying)
from tastytrade.order import (InstrumentType, OrderChain, PlacedComplexOrder,
                              PlacedOrder, PriceEffect)
from tastytrade.session import Session
from tastytrade.utils import TastytradeError, TastytradeJsonDataclass
from tastytrade.watchlists import Watchlist

CERT_STREAMER_URL = 'wss://streamer.cert.tastyworks.com'
STREAMER_URL = 'wss://streamer.tastyworks.com'

DXLINK_VERSION = '0.1-js/1.0.0-beta.4'


class QuoteAlert(TastytradeJsonDataclass):
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


class UnderlyingYearGainSummary(TastytradeJsonDataclass):
    """
    Dataclass that contains information about the yearly gain
    or loss for an underlying
    """
    year: int
    account_number: str
    symbol: str
    instrument_type: InstrumentType
    fees: Decimal
    fees_effect: PriceEffect
    commissions: Decimal
    commissions_effect: PriceEffect
    yearly_realized_gain: Decimal
    yearly_realized_gain_effect: PriceEffect
    realized_lot_gain: Decimal
    realized_lot_gain_effect: PriceEffect


class SubscriptionType(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the subscription types
    for the alert streamer.
    """
    ACCOUNT = 'account-subscribe'  # may be 'connect' in the future
    HEARTBEAT = 'heartbeat'
    PUBLIC_WATCHLISTS = 'public-watchlists-subscribe'
    QUOTE_ALERTS = 'quote-alerts-subscribe'
    USER_MESSAGE = 'user-message-subscribe'


class AlertType(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the event types
    for the account streamer.
    """
    ACCOUNT_BALANCE = 'AccountBalance'
    COMPLEX_ORDER = 'ComplexOrder'
    ORDER = 'Order'
    ORDER_CHAIN = 'OrderChain'
    POSITION = 'CurrentPosition'
    QUOTE_ALERT = 'QuoteAlert'
    TRADING_STATUS = 'TradingStatus'
    UNDERLYING_SUMMARY = 'UnderlyingYearGainSummary'
    WATCHLIST = 'PublicWatchlists'


class AlertStreamer:
    """
    Used to subscribe to account-level updates (balances, orders, positions),
    public watchlist updates, quote alerts, and user-level messages. It should
    always be initialized as an async context manager, or with the `create`
    function, since the object cannot be fully instantiated without async.

    Example usage::

        from tastytrade import Account, AlertStreamer

        async with AlertStreamer(session) as streamer:
            accounts = Account.get_accounts(session)

            # updates to balances, orders, and positions
            await streamer.subscribe_accounts(accounts)
            # changes in public watchlists
            await streamer.subscribe_public_watchlists()
            # quote alerts configured by the user
            await streamer.subscribe_quote_alerts()

            async for data in streamer.listen():
                print(data)

    """
    def __init__(self, session: Session):
        #: The active session used to initiate the streamer or make requests
        self.token: str = session.session_token
        #: The base url for the streamer websocket
        self.base_url: str = (CERT_STREAMER_URL
                              if session.is_test else STREAMER_URL)

        self._queues: Dict[AlertType, Queue] = defaultdict(Queue)
        self._websocket: Optional[WebSocketClientProtocol] = None
        self._connect_task = asyncio.create_task(self._connect())

    async def __aenter__(self):
        time_out = 100
        while not self._websocket:
            await asyncio.sleep(0.1)
            time_out -= 1
            if time_out < 0:
                raise TastytradeError('Connection timed out')

        return self

    @classmethod
    async def create(cls, session: Session) -> 'AlertStreamer':
        self = cls(session)
        return await self.__aenter__()

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def close(self):
        """
        Closes the websocket connection and cancels the heartbeat task.
        """
        self._connect_task.cancel()
        self._heartbeat_task.cancel()

    async def _connect(self) -> None:
        """
        Connect to the websocket server using the URL and authorization
        token provided during initialization.
        """
        headers = {'Authorization': f'Bearer {self.token}'}
        async with websockets.connect(
            self.base_url,
            extra_headers=headers
        ) as websocket:  # type: ignore
            self._websocket = websocket
            self._heartbeat_task = asyncio.create_task(self._heartbeat())

            while True:
                raw_message = await self._websocket.recv()  # type: ignore
                logger.debug('raw message: %s', raw_message)
                data = json.loads(raw_message)
                type_str = data.get('type')
                if type_str is not None:
                    await self._map_message(type_str, data['data'])

    async def listen(
        self,
        event_type: AlertType
    ) -> AsyncIterator[
        Union[
            AccountBalance,
            CurrentPosition,
            PlacedComplexOrder,
            PlacedOrder,
            OrderChain,
            QuoteAlert,
            TradingStatus,
            UnderlyingYearGainSummary,
            Watchlist
        ]
    ]:
        """
        Iterate over non-heartbeat messages received from the streamer,
        mapping them to their appropriate data class and yielding them.
        """
        while True:
            yield await self._queues[event_type].get()

    async def _map_message(
        self,
        type_str: str,
        data: dict
    ):  # pragma: no cover
        """
        I'm not sure what the user-status messages look like,
        so they're absent.
        """
        if type_str == AlertType.ACCOUNT_BALANCE:
            await self._queues[AlertType.ACCOUNT_BALANCE].put(
                AccountBalance(**data)
            )
        elif type_str == AlertType.POSITION:
            await self._queues[AlertType.POSITION].put(
                CurrentPosition(**data)
            )
        elif type_str == AlertType.COMPLEX_ORDER:
            await self._queues[AlertType.COMPLEX_ORDER].put(
                PlacedComplexOrder(**data)
            )
        elif type_str == AlertType.ORDER:
            await self._queues[AlertType.ORDER].put(
                PlacedOrder(**data)
            )
        elif type_str == AlertType.ORDER_CHAIN:
            await self._queues[AlertType.ORDER_CHAIN].put(
                OrderChain(**data)
            )
        elif type_str == AlertType.QUOTE_ALERT:
            await self._queues[AlertType.QUOTE_ALERT].put(
                QuoteAlert(**data)
            )
        elif type_str == AlertType.TRADING_STATUS:
            await self._queues[AlertType.TRADING_STATUS].put(
                TradingStatus(**data)
            )
        elif type_str == AlertType.UNDERLYING_SUMMARY:
            await self._queues[AlertType.UNDERLYING_SUMMARY].put(
                UnderlyingYearGainSummary(**data)
            )
        elif type_str == AlertType.WATCHLIST:
            await self._queues[AlertType.WATCHLIST].put(
                Watchlist(**data)
            )
        else:
            logger.error(f'Unknown message type {type_str}! Please open an '
                         f'issue.\n{data}')

    async def subscribe_accounts(self, accounts: List[Account]) -> None:
        """
        Subscribes to account-level updates (balances, orders, positions).

        :param accounts: list of :class:`Account` to subscribe to updates for
        """
        await self._subscribe(
            SubscriptionType.ACCOUNT,
            [a.account_number for a in accounts]
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
        external_id = session.user['external-id']
        await self._subscribe(SubscriptionType.USER_MESSAGE, value=external_id)

    async def _heartbeat(self) -> None:
        """
        Sends a heartbeat message every 10 seconds to keep the connection
        alive.
        """
        while True:
            await self._subscribe(SubscriptionType.HEARTBEAT, '')
            # send the heartbeat every 10 seconds
            await asyncio.sleep(10)

    async def _subscribe(
        self,
        subscription: SubscriptionType,
        value: Union[Optional[str], List[str]] = ''
    ) -> None:
        """
        Subscribes to a :class:`SubscriptionType`. Depending on the kind of
        subscription, the value parameter may be required.
        """
        message: Dict[str, Any] = {
            'auth-token': self.token,
            'action': subscription
        }
        if value:
            message['value'] = value
        logger.debug('sending alert subscription: %s', message)
        await self._websocket.send(json.dumps(message))  # type: ignore


class DXLinkStreamer:
    """
    A :class:`DXLinkStreamer` object is used to fetch quotes or greeks for a
    given symbol or list of symbols. It should always be initialized as an
    async context manager, or with the `create` function, since the object
    cannot be fully instantiated without async.

    Example usage::

        from tastytrade import DXLinkStreamer
        from tastytrade.dxfeed import EventType

        # must be a production session
        async with DXLinkStreamer(session) as streamer:
            subs = ['SPY']  # list of quotes to subscribe to
            await streamer.subscribe(EventType.QUOTE, subs)
            quote = await streamer.get_event(EventType.QUOTE)
            print(quote)

    """
    def __init__(
        self,
        session: Session,
        ssl_context: SSLContext = create_default_context()
    ):
        self._counter = 0
        self._lock: Lock = Lock()
        self._queues: Dict[EventType, Queue] = defaultdict(Queue)
        self._channels: Dict[EventType, int] = {
            EventType.CANDLE: 1,
            EventType.GREEKS: 3,
            EventType.PROFILE: 5,
            EventType.QUOTE: 7,
            EventType.SUMMARY: 9,
            EventType.THEO_PRICE: 11,
            EventType.TIME_AND_SALE: 13,
            EventType.TRADE: 15,
            EventType.UNDERLYING: 17,
        }
        self._subscription_state: Dict[EventType, str] = \
            defaultdict(lambda: 'CHANNEL_CLOSED')

        #: The unique client identifier received from the server
        self._session = session
        self._authenticated = False
        self._wss_url = session.dxlink_url
        self._auth_token = session.streamer_token
        self._ssl_context = ssl_context

        self._connect_task = asyncio.create_task(self._connect())

    async def __aenter__(self):
        time_out = 100
        while not self._authenticated:
            await asyncio.sleep(0.1)
            time_out -= 1
            if time_out < 0:
                raise TastytradeError('Connection timed out')

        return self

    @classmethod
    async def create(
        cls,
        session: Session,
        ssl_context: SSLContext = create_default_context()
    ) -> 'DXLinkStreamer':
        self = cls(session, ssl_context=ssl_context)
        return await self.__aenter__()

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def close(self):
        """
        Closes the websocket connection and cancels the heartbeat task.
        """
        self._connect_task.cancel()
        self._heartbeat_task.cancel()

    async def _connect(self) -> None:
        """
        Connect to the websocket server using the URL and
        authorization token provided during initialization.
        """

        async with websockets.connect(
            self._wss_url,
            ssl=self._ssl_context
        ) as websocket:
            self._websocket = websocket
            await self._setup_connection()

            # main loop
            while True:
                raw_message = await self._websocket.recv()
                message = json.loads(raw_message)

                logger.debug('received: %s', message)
                if message['type'] == 'SETUP':
                    await self._authenticate_connection()
                elif message['type'] == 'AUTH_STATE':
                    if message['state'] == 'AUTHORIZED':
                        self._authenticated = True
                        self._heartbeat_task = \
                            asyncio.create_task(self._heartbeat())
                elif message['type'] == 'CHANNEL_OPENED':
                    channel = next(k for k, v in self._channels.items()
                                   if v == message['channel'])
                    self._subscription_state[channel] = message['type']
                elif message['type'] == 'CHANNEL_CLOSED':
                    logger.debug('Channel closed: %s', message)
                elif message['type'] == 'FEED_CONFIG':
                    logger.debug('Feed configured: %s', message)
                elif message['type'] == 'FEED_DATA':
                    await self._map_message(message['data'])
                elif message['type'] == 'KEEPALIVE':
                    pass
                else:
                    raise TastytradeError('Unknown message type:', message)

    async def _setup_connection(self):
        message = {
            'type': 'SETUP',
            'channel': 0,
            'keepaliveTimeout': 60,
            'acceptKeepaliveTimeout': 60,
            'version': DXLINK_VERSION
        }
        await self._websocket.send(json.dumps(message))

    async def _authenticate_connection(self):
        message = {
            'type': 'AUTH',
            'channel': 0,
            'token': self._auth_token,
        }
        await self._websocket.send(json.dumps(message))

    async def listen(self, event_type: EventType) -> AsyncIterator[Event]:
        """
        Using the existing subscriptions, pulls events of the given type and
        yield returns them. Never exits unless there's an error or the channel
        is closed.

        :param event_type: the type of event to listen for
        """
        while True:
            yield await self._queues[event_type].get()

    def get_event_nowait(self, event_type: EventType) -> Optional[Event]:
        """
        Using the existing subscriptions, pulls an event of the given type and
        returns it. If the queue is empty None is returned.

        :param event_type: the type of event to get
        """
        if not self._queues[event_type].empty():
            return self._queues[event_type].get_nowait()
        else:
            return None

    async def get_event(self, event_type: EventType) -> Event:
        """
        Using the existing subscription, pulls an event of the given type and
        returns it.

        :param event_type: the type of event to get
        """
        return await self._queues[event_type].get()

    async def _heartbeat(self) -> None:
        """
        Sends a keepalive message every 30 seconds to keep the connection
        alive.
        """
        message = {
            'type': 'KEEPALIVE',
            'channel': 0
        }

        while True:
            logger.debug('sending keepalive message: %s', message)
            await self._websocket.send(json.dumps(message))
            # send the heartbeat every 30 seconds
            await asyncio.sleep(30)

    async def subscribe(
        self,
        event_type: EventType,
        symbols: List[str]
    ) -> None:
        """
        Subscribes to quotes for given list of symbols. Used for recurring data
        feeds.
        For candles, use :meth:`subscribe_candle` instead.

        :param event_type: type of subscription to add
        :param symbols: list of symbols to subscribe for
        """
        if self._subscription_state[event_type] != 'CHANNEL_OPENED':
            await self._channel_request(event_type)
        message = {
            'type': 'FEED_SUBSCRIPTION',
            'channel': self._channels[event_type],
            'add': [{'symbol': symbol, 'type': event_type}
                    for symbol in symbols]
        }
        logger.debug('sending subscription: %s', message)
        await self._websocket.send(json.dumps(message))

    async def cancel_channel(self, event_type: EventType) -> None:
        """
        Cancels the channel for the belonging event_type

        :param event_type: cancel the channel for this event
        """
        message = {
            'type': 'CHANNEL_CANCEL',
            'channel': self._channels[event_type],
        }
        logger.debug('sending channel cancel: %s', message)
        await self._websocket.send(json.dumps(message))

    async def _channel_request(self, event_type: EventType) -> None:
        message = {
            'type': 'CHANNEL_REQUEST',
            'channel': self._channels[event_type],
            'service': 'FEED',
            'parameters': {
                'contract': 'AUTO',
            },
        }
        logger.debug('sending subscription: %s', message)
        await self._websocket.send(json.dumps(message))
        time_out = 100
        while not self._subscription_state[event_type] == 'CHANNEL_OPENED':
            await asyncio.sleep(0.1)
            time_out -= 1
            if time_out <= 0:
                raise TastytradeError('Subscription channel not opened')
        # setup the feed
        await self._channel_setup(event_type)

    async def _channel_setup(self, event_type: EventType) -> None:
        message = {
            'type': 'FEED_SETUP',
            'channel': self._channels[event_type],
            'acceptAggregationPeriod': 10,
            'acceptDataFormat': 'COMPACT'
        }

        def dict_from_schema(event_class: Any):
            schema = event_class.schema()
            return {schema['title']: list(schema['properties'].keys())}

        if event_type == EventType.CANDLE:
            accept = dict_from_schema(Candle)
        elif event_type == EventType.GREEKS:
            accept = dict_from_schema(Greeks)
        elif event_type == EventType.PROFILE:
            accept = dict_from_schema(Profile)
        elif event_type == EventType.QUOTE:
            accept = dict_from_schema(Quote)
        elif event_type == EventType.SUMMARY:
            accept = dict_from_schema(Summary)
        elif event_type == EventType.THEO_PRICE:
            accept = dict_from_schema(TheoPrice)
        elif event_type == EventType.TIME_AND_SALE:
            accept = dict_from_schema(TimeAndSale)
        elif event_type == EventType.TRADE:
            accept = dict_from_schema(Trade)
        elif event_type == EventType.UNDERLYING:
            accept = dict_from_schema(Underlying)
        message['acceptEventFields'] = accept
        # send message
        logger.debug('setting up feed: %s', message)
        await self._websocket.send(json.dumps(message))

    async def unsubscribe(
        self,
        event_type: EventType,
        symbols: List[str]
    ) -> None:
        """
        Removes existing subscription for given list of symbols.
        For candles, use :meth:`unsubscribe_candle` instead.

        :param event_type: type of subscription to remove
        :param symbols: list of symbols to unsubscribe from
        """
        if not self._authenticated:
            raise TastytradeError('Stream not authenticated')
        event_type_str = str(event_type).split('.')[1].capitalize()
        message = {
            'type': 'FEED_SUBSCRIPTION',
            'channel': self._channels[event_type],
            'remove': [{'symbol': symbol, "type": event_type_str} for symbol in
                       symbols]
        }
        logger.debug('sending subscription: %s', message)
        await self._websocket.send(json.dumps(message))

    async def subscribe_candle(
        self,
        symbols: List[str],
        interval: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        extended_trading_hours: bool = False
    ) -> None:
        """
        Subscribes to time series data for the given symbol.

        :param symbols: list of symbols to get data for
        :param interval:
            the width of each candle in time, e.g. '15s', '5m', '1h', '3d',
            '1w', '1mo'
        :param start_time: starting time for the data range
        :param end_time: ending time for the data range
        :param extended_trading_hours: whether to include extended trading
        """
        if self._subscription_state[EventType.CANDLE] != 'CHANNEL_OPENED':
            await self._channel_request(EventType.CANDLE)
        message = {
            'type': 'FEED_SUBSCRIPTION',
            'channel': self._channels[EventType.CANDLE],
            'add': [{
                'symbol': (f'{ticker}{{={interval}}}' if extended_trading_hours
                           else f'{ticker}{{={interval},tho=true}}'),
                'type': 'Candle',
                'fromTime': int(start_time.timestamp() * 1000)
            } for ticker in symbols]
        }
        if end_time is not None:
            raise TastytradeError('End time no longer supported')
        await self._websocket.send(json.dumps(message))

    async def unsubscribe_candle(
        self,
        ticker: str,
        interval: Optional[str] = None,
        extended_trading_hours: bool = False
    ) -> None:
        """
        Removes existing subscription for a candle.

        :param ticker: symbol to unsubscribe from
        :param interval: candle width to unsubscribe from
        :param extended_trading_hours:
            whether candle to unsubscribe from contains extended trading hours
        """
        message = {
            'type': 'FEED_SUBSCRIPTION',
            'channel': self._channels[EventType.CANDLE],
            'remove': [{
                'symbol': (f'{ticker}{{={interval}}}' if extended_trading_hours
                           else f'{ticker}{{={interval},tho=true}}'),
                'type': 'Candle'
            }]
        }
        await self._websocket.send(json.dumps(message))

    async def _map_message(self, message) -> None:  # pragma: no cover
        """
        Takes the raw JSON data, parses the events and places them into their
        respective queues.

        :param message: raw JSON data from the websocket
        """
        logger.debug('received message: %s', message)
        if isinstance(message[0], str):
            msg_type = message[0]
        else:
            msg_type = message[0][0]
        data = message[1]
        # parse type or warn for unknown type
        if msg_type == EventType.CANDLE:
            candles = Candle.from_stream(data)
            for candle in candles:
                await self._queues[EventType.CANDLE].put(candle)
        elif msg_type == EventType.GREEKS:
            greeks = Greeks.from_stream(data)
            for greek in greeks:
                await self._queues[EventType.GREEKS].put(greek)
        elif msg_type == EventType.PROFILE:
            profiles = Profile.from_stream(data)
            for profile in profiles:
                await self._queues[EventType.PROFILE].put(profile)
        elif msg_type == EventType.QUOTE:
            quotes = Quote.from_stream(data)
            for quote in quotes:
                await self._queues[EventType.QUOTE].put(quote)
        elif msg_type == EventType.SUMMARY:
            summaries = Summary.from_stream(data)
            for summary in summaries:
                await self._queues[EventType.SUMMARY].put(summary)
        elif msg_type == EventType.THEO_PRICE:
            theo_prices = TheoPrice.from_stream(data)
            for theo_price in theo_prices:
                await self._queues[EventType.THEO_PRICE].put(theo_price)
        elif msg_type == EventType.TIME_AND_SALE:
            time_and_sales = TimeAndSale.from_stream(data)
            for tas in time_and_sales:
                await self._queues[EventType.TIME_AND_SALE].put(tas)
        elif msg_type == EventType.TRADE:
            trades = Trade.from_stream(data)
            for trade in trades:
                await self._queues[EventType.TRADE].put(trade)
        elif msg_type == EventType.UNDERLYING:
            underlyings = Underlying.from_stream(data)
            for underlying in underlyings:
                await self._queues[EventType.UNDERLYING].put(underlying)
        else:
            raise TastytradeError(f'Unknown message type received: {message}')
