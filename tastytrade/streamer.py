import asyncio
import json
from asyncio import Lock, Queue
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, AsyncIterator, Dict, List, Optional, Union

import websockets

from tastytrade import logger
from tastytrade.account import (Account, AccountBalance, CurrentPosition,
                                TradingStatus)
from tastytrade.dxfeed import (Candle, Channel, Event, EventType, Greeks,
                               Profile, Quote, Summary, TheoPrice, TimeAndSale,
                               Trade, Underlying)
from tastytrade.order import (InstrumentType, OrderChain, PlacedOrder,
                              PriceEffect)
from tastytrade.session import CertificationSession, ProductionSession, Session
from tastytrade.utils import TastytradeError, TastytradeJsonDataclass
from tastytrade.watchlists import Watchlist

CERT_STREAMER_URL = 'wss://streamer.cert.tastyworks.com'
STREAMER_URL = 'wss://streamer.tastyworks.com'


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


class AccountStreamer:
    """
    Used to subscribe to account-level updates (balances, orders, positions),
    public watchlist updates, quote alerts, and user-level messages. It should
    always be initialized as an async context manager, or with the `create`
    function, since the object cannot be fully instantiated without async.

    Example usage::

        from tastytrade import Account, AccountStreamer

        async with AccountStreamer(session) as streamer:
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
        is_certification = isinstance(session, CertificationSession)
        self.base_url: str = \
            CERT_STREAMER_URL if is_certification else STREAMER_URL

        self._queue: Queue = Queue()
        self._websocket = None
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
    async def create(cls, session: Session) -> 'AccountStreamer':
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
        async with websockets.connect(  # type: ignore
            self.base_url,
            extra_headers=headers
        ) as websocket:
            self._websocket = websocket
            self._heartbeat_task = asyncio.create_task(self._heartbeat())

            while True:
                raw_message = await self._websocket.recv()  # type: ignore
                logger.debug('raw message: %s', raw_message)
                await self._queue.put(json.loads(raw_message))

    async def listen(self) -> AsyncIterator[TastytradeJsonDataclass]:
        """
        Iterate over non-heartbeat messages received from the streamer,
        mapping them to their appropriate data class and yielding them.
        """
        while True:
            data = await self._queue.get()
            type_str = data.get('type')
            if type_str is not None:
                yield self._map_message(type_str, data['data'])

    def _map_message(
        self,
        type_str: str,
        data: dict
    ) -> TastytradeJsonDataclass:
        """
        I'm not sure what the user-status messages look like,
        so they're absent.
        """
        if type_str == 'AccountBalance':
            return AccountBalance(**data)
        elif type_str == 'CurrentPosition':
            return CurrentPosition(**data)
        elif type_str == 'Order':
            return PlacedOrder(**data)
        elif type_str == 'OrderChain':
            return OrderChain(**data)
        elif type_str == 'QuoteAlert':
            return QuoteAlert(**data)
        elif type_str == 'TradingStatus':
            return TradingStatus(**data)
        elif type_str == 'UnderlyingYearGainSummary':
            return UnderlyingYearGainSummary(**data)
        elif type_str == 'PublicWatchlists':
            return Watchlist(**data)
        else:
            raise TastytradeError(f'Unknown message type: {type_str}\n{data}')

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


class DXFeedStreamer:  # pragma: no cover
    """
    A :class:`DXFeedStreamer` object is used to fetch quotes or greeks for a
    given symbol or list of symbols. It should always be initialized as an
    async context manager, or with the `create` function, since the object
    cannot be fully instantiated without async.

    Example usage::

        from tastytrade import DXFeedStreamer
        from tastytrade.dxfeed import EventType

        # must be a production session
        async with DXFeedStreamer(session) as streamer:
            subs = ['SPY', 'GLD']  # list of quotes to fetch
            await streamer.subscribe(EventType.QUOTE, subs)
            quote = await streamer.get_event(EventType.QUOTE)
            print(quote)

    """
    def __init__(self, session: ProductionSession):
        self._counter = 0
        self._lock: Lock = Lock()
        self._queues: Dict[EventType, Queue] = defaultdict(Queue)
        #: The unique client identifier received from the server
        self.client_id: Optional[str] = None

        self._auth_token = session.streamer_token
        self._wss_url = session.dxfeed_url

        self._connect_task = asyncio.create_task(self._connect())

    async def __aenter__(self):
        time_out = 100
        while not self.client_id:
            await asyncio.sleep(0.1)
            time_out -= 1
            if time_out < 0:
                raise TastytradeError('Connection timed out')

        return self

    @classmethod
    async def create(cls, session: ProductionSession) -> 'DXFeedStreamer':
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

    async def _next_id(self):
        async with self._lock:
            self._counter += 1
        return self._counter

    async def _connect(self) -> None:
        """
        Connect to the websocket server using the URL and
        authorization token provided during initialization.
        """
        headers = {'Authorization': f'Bearer {self._auth_token}'}

        async with websockets.connect(  # type: ignore
            self._wss_url,
            extra_headers=headers
        ) as websocket:
            self._websocket = websocket
            await self._handshake()

            while not self.client_id:
                raw_message = await self._websocket.recv()
                message = json.loads(raw_message)[0]

                logger.debug('received: %s', message)
                if message['channel'] == Channel.HANDSHAKE:
                    if message['successful']:
                        self.client_id = message['clientId']
                        self._heartbeat_task = \
                            asyncio.create_task(self._heartbeat())
                    else:
                        raise TastytradeError('Handshake failed')

            # main loop
            while True:
                raw_message = await self._websocket.recv()
                message = json.loads(raw_message)[0]

                if (message['channel'] == Channel.DATA or
                        message['channel'] == Channel.TIME_SERIES):
                    logger.debug('data received: %s', message)
                    await self._map_message(message['data'])
                elif message['channel'] == Channel.SUBSCRIPTION:
                    logger.debug('sub received: %s', message)

    async def _handshake(self) -> None:
        """
        Sends a handshake message to the specified WebSocket
        connection. The handshake message is sent as a JSON
        encoded array with a single element, containing the
        handshake message as its only element.
        """
        id = await self._next_id()
        message = {
            'id': id,
            'version': '1.0',
            'minimumVersion': '1.0',
            'channel': Channel.HANDSHAKE,
            'supportedConnectionTypes': [
                'websocket',
                'long-polling',
                'callback-polling'
            ],
            'ext': {'com.devexperts.auth.AuthToken': self._auth_token},
            'advice': {
                'timeout': 60000,
                'interval': 0
            }
        }
        await self._websocket.send(json.dumps([message]))

    async def listen(self, event_type: EventType) -> AsyncIterator[Event]:
        """
        Using the existing subscriptions, pulls events of the given type and
        yield returns them. Never exits unless there's an error or the channel
        is closed.

        :param event_type: the type of event to listen for
        """
        while True:
            yield await self._queues[event_type].get()

    async def get_event(self, event_type: EventType) -> Event:
        """
        Using the existing subscription , pulls an event of the given type and
        returns it.

        :param event_type: the type of event to get
        """
        while True:
            return await self._queues[event_type].get()

    async def _heartbeat(self) -> None:
        """
        Sends a heartbeat message every 10 seconds to keep the connection
        alive.
        """
        while True:
            id = await self._next_id()
            message = {
                'id': id,
                'channel': Channel.HEARTBEAT,
                'clientId': self.client_id,
                'connectionType': 'websocket'
            }
            logger.debug('sending heartbeat: %s', message)
            await self._websocket.send(json.dumps([message]))
            # send the heartbeat every 10 seconds
            await asyncio.sleep(10)

    async def subscribe(
        self,
        event_type: EventType,
        symbols: List[str],
        reset: bool = False
    ) -> None:
        """
        Subscribes to quotes for given list of symbols. Used for recurring data
        feeds.
        For candles, use :meth:`subscribe_candle` instead.

        :param event_type: type of subscription to add
        :param symbols: list of symbols to subscribe for
        :param reset:
            whether to reset the subscription list (remove all other
            subscriptions of all types)
        """
        id = await self._next_id()
        message = {
            'id': id,
            'channel': Channel.SUBSCRIPTION,
            'data': {
                'reset': reset,
                'add': {event_type: symbols}
            },
            'clientId': self.client_id
        }
        logger.debug('sending subscription: %s', message)
        await self._websocket.send(json.dumps([message]))

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
        id = await self._next_id()
        message = {
            'id': id,
            'channel': Channel.SUBSCRIPTION,
            'data': {'remove': {event_type: symbols}},
            'clientId': self.client_id
        }
        logger.debug('sending unsubscription: %s', message)
        await self._websocket.send(json.dumps([message]))

    async def subscribe_candle(
        self,
        symbols: List[str],
        interval: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        extended_trading_hours: bool = False,
        reset: bool = False
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
        :param reset: whether to reset the subscription list
        """
        id = await self._next_id()
        key = EventType.CANDLE
        message = {
            'id': id,
            'channel': Channel.SUBSCRIPTION,
            'data': {
                'reset': reset,
                'addTimeSeries': {
                    key: [{
                        'eventSymbol': f'{ticker}{{={interval},tho=true}}'
                        if extended_trading_hours
                        else f'{ticker}{{={interval}}}',
                        'fromTime': int(start_time.timestamp() * 1000)
                    } for ticker in symbols]
                }
            },
            'clientId': self.client_id
        }
        if end_time is not None:
            message['data']['addTimeSeries'][key][0]['toTime'] = \
                int(end_time.timestamp() * 1000)
        await self._websocket.send(json.dumps([message]))

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
        id = await self._next_id()
        message = {
            'id': id,
            'channel': Channel.SUBSCRIPTION,
            'data': {
                'removeTimeSeries': {
                    EventType.CANDLE: [
                        f'{ticker}{{={interval},tho=true}}'
                        if extended_trading_hours
                        else f'{ticker}{{={interval}}}'
                    ]
                }
            },
            'clientId': self.client_id
        }
        logger.debug('sending unsubscription: %s', message)
        await self._websocket.send(json.dumps([message]))

    async def _map_message(self, message) -> None:
        """
        Takes the raw JSON data, parses the events and places them into their
        respective queues.

        :param message: raw JSON data from the websocket
        """
        # the first time around, types are shown
        if isinstance(message[0], str):
            msg_type = message[0]
        else:
            msg_type = message[0][0]
        # regardless, the second element will be the raw data
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
    def __init__(self, session: ProductionSession):
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
    async def create(cls, session: ProductionSession) -> 'DXLinkStreamer':
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
        Connect to the websocket server using the URL and
        authorization token provided during initialization.
        """

        async with websockets.connect(  # type: ignore
            self._wss_url
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
                    channel = next((k for k, v in self._channels.items()
                                    if v == message['channel']))
                    self._subscription_state[channel] \
                        = message['type']
                elif message['type'] == 'CHANNEL_CLOSED':
                    pass
                elif message['type'] == 'FEED_CONFIG':
                    pass
                elif message['type'] == 'FEED_DATA':
                    await self._map_message(message['data'])
                elif message['type'] == 'KEEPALIVE':
                    pass
                else:
                    raise TastytradeError(message)

    async def _setup_connection(self):
        message = {
            'type': 'SETUP',
            'channel': 0,
            'keepaliveTimeout': 60,
            'acceptKeepaliveTimeout': 60,
            'version': '0.1-js/1.0.0'
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

    async def get_event(self, event_type: EventType) -> Event:
        """
        Using the existing subscription, pulls an event of the given type and
        returns it.

        :param event_type: the type of event to get
        """
        while True:
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
        await self._channel_request(event_type)
        event_type_str = str(event_type).split('.')[1].capitalize()
        message = {
            'type': 'FEED_SUBSCRIPTION',
            'channel': self._channels[event_type],
            'add': [{'symbol': symbol, "type": event_type_str}
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
        await self._channel_request(EventType.CANDLE)
        message = {
            'type': 'FEED_SUBSCRIPTION',
            'channel': self._channels[EventType.CANDLE],
            'add': [{
                'symbol': f'{ticker}{{={interval},tho=true}}'
                if extended_trading_hours
                else f'{ticker}{{={interval}}}',
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
        await self._channel_request(EventType.CANDLE)
        message = {
            'type': 'FEED_SUBSCRIPTION',
            'channel': self._channels[EventType.CANDLE],
            'remove': [{
                'symbol': f'{ticker}{{={interval},tho=true}}'
                if extended_trading_hours
                else f'{ticker}{{={interval}}}',
                'type': 'Candle',
            }]
        }
        await self._websocket.send(json.dumps(message))

    async def _map_message(self, message) -> None:
        """
        Takes the raw JSON data, parses the events and places them into their
        respective queues.

        :param message: raw JSON data from the websocket
        """
        for item in message:
            msg_type = item.pop('eventType')
            # parse type or warn for unknown type
            if msg_type == EventType.CANDLE:
                await self._queues[EventType.CANDLE].put(Candle(**item))
            elif msg_type == EventType.GREEKS:
                await self._queues[EventType.GREEKS].put(Greeks(**item))
            elif msg_type == EventType.PROFILE:
                await self._queues[EventType.PROFILE].put(Profile(**item))
            elif msg_type == EventType.QUOTE:
                await self._queues[EventType.QUOTE].put(Quote(**item))
            elif msg_type == EventType.SUMMARY:
                await self._queues[EventType.SUMMARY].put(Summary(**item))
            elif msg_type == EventType.THEO_PRICE:
                await self._queues[EventType.THEO_PRICE].put(TheoPrice(**item))
            elif msg_type == EventType.TIME_AND_SALE:
                tas = TimeAndSale(**item)
                await self._queues[EventType.TIME_AND_SALE].put(tas)
            elif msg_type == EventType.TRADE:
                await self._queues[EventType.TRADE].put(Trade(**item))
            elif msg_type == EventType.UNDERLYING:
                undl = Underlying(**item)
                await self._queues[EventType.UNDERLYING].put(undl)
            else:
                raise TastytradeError(f'Unknown message type: {message}')
