import asyncio
import json
from asyncio import Lock, Queue
from datetime import datetime
from enum import Enum
from typing import Any, AsyncIterator, Optional

import requests
import websockets

from tastytrade import logger
from tastytrade.account import Account
from tastytrade.dxfeed import Channel
from tastytrade.dxfeed.candle import Candle
from tastytrade.dxfeed.event import Event, EventType
from tastytrade.dxfeed.greeks import Greeks
from tastytrade.dxfeed.profile import Profile
from tastytrade.dxfeed.quote import Quote
from tastytrade.dxfeed.summary import Summary
from tastytrade.dxfeed.theoprice import TheoPrice
from tastytrade.dxfeed.trade import Trade
from tastytrade.session import Session
from tastytrade.utils import TastytradeError, validate_response

CERT_STREAMER_URL = 'wss://streamer.cert.tastyworks.com'
STREAMER_URL = 'wss://streamer.tastyworks.com'


class SubscriptionType(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the subscription types for the alert streamer.
    """
    ACCOUNT = 'account-subscribe'  # 'account-subscribe' may be deprecated in the future
    HEARTBEAT = 'heartbeat'
    PUBLIC_WATCHLISTS = 'public-watchlists-subscribe'
    QUOTE_ALERTS = 'quote-alerts-subscribe'
    USER_MESSAGE = 'user-message-subscribe'


class AlertStreamer:
    """
    Used to subscribe to account-level updates (balances, orders, positions), public
    watchlist updates, quote alerts, and user-level messages. It should always be
    initialized using the :meth:`create` function, since the object cannot be fully
    instantiated without using async.

    Example usage::

        session = Session('user', 'pass')
        streamer = await AlertStreamer.create(session)
        accounts = Account.get_accounts(session)

        await streamer.account_subscribe(accounts)
        await streamer.public_watchlists_subscribe()
        await streamer.quote_alerts_subscribe()
        await streamer.user_message_subscribe(session)

        async for data in streamer.listen():
            print(data)

    """
    def __init__(self, session: Session):
        #: The active session used to initiate the streamer or make requests
        self.token: str = session.session_token
        #: The base url for the streamer websocket
        self.base_url: str = CERT_STREAMER_URL if session.is_certification else STREAMER_URL

        self._done = False
        self._queue: Queue = Queue()
        self._websocket = None

        self._connect_task = asyncio.create_task(self._connect())

    @classmethod
    async def create(cls, session: Session) -> 'AlertStreamer':
        """
        Factory method for the :class:`DataStreamer` object. Simply calls the
        constructor and performs the asynchronous setup tasks. This should be used
        instead of the constructor.

        :param session: active user session to use
        """
        self = cls(session)
        while not self._websocket:
            await asyncio.sleep(0.1)

        return self

    async def _connect(self) -> None:
        """
        Connect to the websocket server using the URL and authorization token provided
        during initialization.
        """
        headers = {'Authorization': f'Bearer {self.token}'}
        async with websockets.connect(self.base_url, extra_headers=headers) as websocket:  # type: ignore
            self._websocket = websocket
            self._heartbeat_task = asyncio.create_task(self._heartbeat())

            while not self._done:
                raw_message = await self._websocket.recv()  # type: ignore
                logger.debug('raw message: %s', raw_message)
                await self._queue.put(json.loads(raw_message))

    async def listen(self) -> AsyncIterator[Any]:
        """
        Iterate over non-heartbeat messages received from the streamer.
        """
        while True:
            data = await self._queue.get()
            if data.get('action') != SubscriptionType.HEARTBEAT:
                yield data

    async def account_subscribe(self, accounts: list[Account]) -> None:
        """
        Subscribes to account-level updates (balances, orders, positions).

        :param accounts: list of :class:`tastytrade.account.Account`s to subscribe to updates for
        """
        await self._subscribe(SubscriptionType.ACCOUNT, [acc.account_number for acc in accounts])

    async def public_watchlists_subscribe(self) -> None:
        """
        Subscribes to public watchlist updates.
        """
        await self._subscribe(SubscriptionType.PUBLIC_WATCHLISTS)

    async def quote_alerts_subscribe(self) -> None:
        """
        Subscribes to quote alerts (which are configured at a user level).
        """
        await self._subscribe(SubscriptionType.QUOTE_ALERTS)

    async def user_message_subscribe(self, session: Session) -> None:
        """
        Subscribes to user-level messages.
        """
        external_id = session.user['external-id']
        await self._subscribe(SubscriptionType.USER_MESSAGE, value=external_id)

    async def close(self) -> None:
        """
        Closes the websocket connection and cancels the heartbeat task.
        """
        self._done = True
        await asyncio.gather(self._connect_task, self._heartbeat_task)

    async def _heartbeat(self) -> None:
        """
        Sends a heartbeat message every 10 seconds to keep the connection alive.
        """
        while not self._done:
            await self._subscribe(SubscriptionType.HEARTBEAT, '')
            # send the heartbeat every 10 seconds
            await asyncio.sleep(10)

    async def _subscribe(self, subscription: SubscriptionType, value: Optional[str] | list[str] = '') -> None:
        """
        Subscribes to one of the :class:`SubscriptionType`s. Depending on the kind of
        subscription, the value parameter may be required.
        """
        message: dict[str, Any] = {
            'auth-token': self.token,
            'action': subscription
        }
        if value:
            message['value'] = value
        logger.debug('sending alert subscription: %s', message)
        await self._websocket.send(json.dumps(message))  # type: ignore


class DataStreamer:
    """
    A :class:`DataStreamer` object is used to fetch quotes or greeks for a given symbol
    or list of symbols. It should always be initialized using the :meth:`create` function,
    since the object cannot be fully instantiated without using async.

    Example usage::

        session = Session('user', 'pass')
        streamer = await DataStreamer.create(session)

        subs = ['SPY', 'GLD']  # list of quotes to fetch
        quote = await streamer.oneshot(EventType.QUOTE, subs)

    """
    def __init__(self, session: Session):
        #: The active session used to initiate the streamer or make requests
        self.session: Session = session

        self._counter = 0
        self._lock: Lock = Lock()
        self._queue: Queue = Queue()
        self._queue_candle: Queue = Queue()
        self._done = False
        #: The unique client identifier received from the server
        self.client_id: Optional[str] = None

        response = requests.get(f'{session.base_url}/quote-streamer-tokens', headers=session.headers)
        validate_response(response)
        logger.debug('response %s', json.dumps(response.json()))
        self._auth_token = response.json()['data']['token']
        url = response.json()['data']['websocket-url'] + '/cometd'
        self._wss_url = url.replace('https', 'wss')

        self._connect_task = asyncio.create_task(self._connect())

    @classmethod
    async def create(cls, session: Session) -> 'DataStreamer':
        """
        Factory method for the :class:`DataStreamer` object. Simply calls the
        constructor and performs the asynchronous setup tasks. This should be used
        instead of the constructor.

        :param session: active user session to use
        """
        self = cls(session)
        while not self.client_id:
            await asyncio.sleep(0.1)

        return self

    async def _next_id(self):
        async with self._lock:
            self._counter += 1
        return self._counter

    async def _connect(self) -> None:
        """
        Connect to the websocket server using the URL and authorization token provided
        during initialization.
        """
        headers = {'Authorization': f'Bearer {self._auth_token}'}

        async with websockets.connect(self._wss_url, extra_headers=headers) as websocket:  # type: ignore
            self._websocket = websocket
            await self._handshake()

            while not self.client_id:
                raw_message = await self._websocket.recv()
                message = json.loads(raw_message)[0]

                logger.debug('received: %s', message)
                if message['channel'] == Channel.HANDSHAKE:
                    if message['successful']:
                        self.client_id = message['clientId']
                        self._heartbeat_task = asyncio.create_task(self._heartbeat())
                    else:
                        raise TastytradeError('Handshake failed')

            while not self._done:
                raw_message = await self._websocket.recv()
                message = json.loads(raw_message)[0]

                if message['channel'] == Channel.DATA:
                    logger.debug('data received: %s', message)
                    await self._queue.put(message['data'])
                elif message['channel'] == Channel.CANDLE:
                    logger.debug('candle received: %s', message)
                    await self._queue_candle.put(message['data'])
                elif message['channel'] == Channel.SUBSCRIPTION:
                    logger.debug('sub received: %s', message)

    async def _handshake(self) -> None:
        """
        Sends a handshake message to the specified WebSocket connection. The handshake
        message is sent as a JSON-encoded array with a single element, containing the
        handshake message as its only element.
        """
        id = await self._next_id()
        message = {
            'id': id,
            'version': '1.0',
            'minimumVersion': '1.0',
            'channel': Channel.HANDSHAKE,
            'supportedConnectionTypes': ['websocket', 'long-polling', 'callback-polling'],
            'ext': {'com.devexperts.auth.AuthToken': self._auth_token},
            'advice': {
                'timeout': 60000,
                'interval': 0
            }
        }
        await self._websocket.send(json.dumps([message]))

    async def listen(self) -> AsyncIterator[Event]:
        """
        Using the existing subscriptions, pulls :class:`~tastytrade.dxfeed.event.Event`s and yield returns
        them. Never exits unless there's an error or the channel is closed.
        """
        while True:
            raw_data = await self._queue.get()
            messages = _map_message(raw_data)
            for message in messages:
                yield message

    async def listen_candle(self) -> AsyncIterator[Candle]:
        """
        Using the existing subscriptions, pulls candles and yield returns them.
        Never exits unless there's an error or the channel is closed.
        """
        while True:
            raw_data = await self._queue_candle.get()
            messages = _map_message(raw_data)
            for message in messages:
                yield message  # type: ignore

    async def close(self) -> None:
        """
        Closes the websocket connection and cancels the heartbeat task.
        """
        self._done = True
        await asyncio.gather(self._connect_task, self._heartbeat_task)

    async def _heartbeat(self) -> None:
        """
        Sends a heartbeat message every 10 seconds to keep the connection alive.
        """
        while not self._done:
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

    async def subscribe(self, event_type: EventType, symbols: list[str], reset: bool = False) -> None:
        """
        Subscribes to quotes for given list of symbols. Used for recurring data feeds;
        if you just want to get a one-time quote, use :meth:`oneshot`.

        :param event_type: type of subscription to add
        :param symbols: list of symbols to subscribe for
        :param reset:
            whether to reset the subscription list (remove all other subscriptions of all types)
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

    async def unsubscribe(self, event_type: EventType, symbols: list[str]) -> None:
        """
        Removes existing subscription for given list of symbols.

        :param event_type: type of subscription to remove
        :param symbols: list of symbols to unsubscribe from
        """
        id = await self._next_id()
        message = {
            'id': id,
            'channel': Channel.SUBSCRIPTION,
            'data': {
                'reset': False,
                'remove': {event_type: symbols}
            },
            'clientId': self.client_id
        }
        logger.debug('sending unsubscription: %s', message)
        await self._websocket.send(json.dumps([message]))

    async def oneshot(self, event_type: EventType, symbols: list[str]) -> list[Event]:
        """
        Using the given information, subscribes to the list of symbols passed, streams
        the requested information once, then unsubscribes. If you want to maintain the
        subscription open, add a subscription with :meth:`subscribe` and listen with
        :meth:`listen`.

        If you use this alongside :meth:`subscribe` and :meth:`listen`, you will get
        some unexpected behavior. Most apps should use either this or :meth:`listen`
        but not both.

        :param event_type: the type of subscription to stream, either greeks or quotes
        :param symbols: list of symbols to subscribe to

        :return: list of :class:`~tastytrade.dxfeed.event.Event`s pulled.
        """
        await self.subscribe(event_type, symbols)
        data = []
        async for item in self.listen():
            data.append(item)
            if len(data) >= len(symbols):
                break
        await self.unsubscribe(event_type, symbols)
        return data

    async def subscribe_candle(self, ticker: str, start_time: datetime, interval: str) -> None:
        """
        Subscribes to candle-style 'OHLC' data for the given symbol.

        :param ticker: symbol to get date for
        :param start_time: starting time for the data range
        :param interval: the width of each candle in time, e.g. '5m', '1h', '3d', '1w', '1mo'
        """
        id = await self._next_id()
        message = {
            'id': id,
            'channel': Channel.SUBSCRIPTION,
            'data': {
                'addTimeSeries': {
                    'Candle': [{
                        'eventSymbol': f'{ticker}{{={interval}}}',
                        'fromTime': int(start_time.timestamp() * 1000)
                    }]
                }
            },
            'clientId': self.client_id
        }
        logger.debug('sending subscription: %s', message)
        await self._websocket.send(json.dumps([message]))

    async def unsubscribe_candle(self, ticker: str, interval: str) -> None:
        """
        Removes existing :class:`~tastytrade.dxfeed.event.Candle` subscription for given list of symbols.

        :param ticker: symbol to unsubscribe from
        :param interval: candle width to unsubscribe from
        """
        id = await self._next_id()
        message = {
            'id': id,
            'channel': Channel.SUBSCRIPTION,
            'data': {
                'removeTimeSeries': {'Candle': [f'{ticker}{{={interval}}}']}
            },
            'clientId': self.client_id
        }
        logger.debug('sending unsubscription: %s', message)
        await self._websocket.send(json.dumps([message]))

    async def oneshot_candle(self, ticker: str, start_time: datetime, interval: str) -> list[Candle]:
        """
        Subscribes to candle-style 'OHLC' data for the given symbol, waits for
        the complete range to be received, then unsubscribes.

        :param ticker: symbol to get date for
        :param start_time: starting time for the data range
        :param interval: the width of each candle in time, e.g. '5m', '1h', '3d', '1w', '1mo'
        """
        await self.subscribe_candle(ticker, start_time, interval)
        candles = []
        async for candle in self.listen_candle():
            candles.append(candle)
            # until we hit the start date, keep going
            if datetime.fromtimestamp(candle.time / 1000) <= start_time:
                break
        await self.unsubscribe_candle(ticker, interval)

        candles.reverse()
        return candles


def _map_message(message) -> list[Event]:
    """
    Takes the raw JSON data and returns a list of parsed :class:`~tastytrade.dxfeed.event.Event` objects.
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
        res = Candle.from_stream(data)
    elif msg_type == EventType.GREEKS:
        res = Greeks.from_stream(data)
    elif msg_type == EventType.PROFILE:
        res = Profile.from_stream(data)
    elif msg_type == EventType.QUOTE:
        res = Quote.from_stream(data)
    elif msg_type == EventType.SUMMARY:
        res = Summary.from_stream(data)
    elif msg_type == EventType.THEO_PRICE:
        res = TheoPrice.from_stream(data)
    elif msg_type == EventType.TRADE:
        res = Trade.from_stream(data)
    else:
        raise TastytradeError(f'Unknown message type received from streamer: {message}')

    return res
