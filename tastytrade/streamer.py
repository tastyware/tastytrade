import asyncio
from typing import AsyncIterator

import json
import requests
import websockets

from tastytrade import logger
from tastytrade.dxfeed import Channel
from tastytrade.dxfeed.event import Event, EventType
from tastytrade.dxfeed.greeks import Greeks
from tastytrade.dxfeed.profile import Profile
from tastytrade.dxfeed.quote import Quote
from tastytrade.dxfeed.summary import Summary
from tastytrade.dxfeed.theoprice import TheoPrice
from tastytrade.dxfeed.trade import Trade
from tastytrade.session import Session
from tastytrade.utils import TastytradeError, validate_response


class DataStreamer:
    """
    A :class:`DataStreamer` object is used to fetch quotes or greeks for a given symbol
    or list of symbols. It should always be initialized using the :meth:`create` function,
    since the object cannot be fully instantiated without using async.

    :param session: active user session to use

    Example usage::

        session = Session('user', 'pass')
        streamer = await DataStreamer.create(session)

        subs = ['SPY', 'GLD']  # list of quotes to fetch
        quote = await streamer.stream(EventType.QUOTE, subs)

    """
    def __init__(self, session: Session):
        #: The active session used to initiate the streamer or make requests
        self.session: Session = session

        self._counter = 0
        self._lock = asyncio.Lock()
        self._queue = asyncio.Queue()
        self._done = False
        #: The unique client identifier received from the server
        self.client_id = None
        
        response = requests.get(f'{session.base_url}/quote-streamer-tokens', headers=session.headers)
        validate_response(response)
        logger.debug('response %s', json.dumps(response.json()))
        self._auth_token = response.json()['data']['token']
        url = response.json()['data']['websocket-url'] + '/cometd'
        self._wss_url = url.replace('https', 'wss')

    @classmethod
    async def create(cls, session: Session) -> 'DataStreamer':
        """
        Factory method for the :class:`DataStreamer` object. Simply calls the
        constructor and performs the asynchronous setup tasks. This should be used
        instead of the constructor.

        :param session: active user session to use
        """
        self = cls(session)
        self._connect_task = asyncio.create_task(self._connect())
        while not self.client_id:
            await asyncio.sleep(0.25)

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
        headers = {'Authorization': 'Bearer ' + self._auth_token}

        async with websockets.connect(self._wss_url, extra_headers=headers) as websocket:
            self.websocket = websocket
            await self._handshake()

            while not self.client_id:
                raw_message = await self.websocket.recv()
                message = json.loads(raw_message)[0]
                
                logger.debug('received: %s', message)
                if message['channel'] == Channel.HANDSHAKE:
                    if message['successful']:
                        self.client_id = message['clientId']
                        self._heartbeat_task = asyncio.create_task(self._heartbeat())
                    else:
                        raise TastytradeError('Handshake failed')
        
            while not self._done:
                raw_message = await self.websocket.recv()
                message = json.loads(raw_message)[0]
                
                if message['channel'] == Channel.DATA:
                    logger.debug('queueing received: %s', message)
                    await self._queue.put(message['data'])
                elif message['channel'] == Channel.SUBSCRIPTION:
                    logger.debug('sub received: %s', message)

    async def _handshake(self) -> None:
        """
        Sends a handshake message to the specified WebSocket connection.

        The handshake message is a JSON-encoded dictionary with the following keys:
        - id: a unique identifier for the message
        - version: the version of the Bayeux protocol used
        - minimumVersion: the minimum version of the Bayeux protocol supported
        - channel: the channel to which the message is being sent
        - supportedConnectionTypes: a list of supported connection types
        - ext: an extension dictionary containing additional data
        - advice: an advice dictionary with the following keys:
            - timeout: the maximum time to wait for a response
            - interval: the minimum time between retries

        The handshake message is sent as a JSON-encoded array with a single element,
        containing the handshake message as its only element.
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
        await self.websocket.send(json.dumps([message]))

    async def listen(self) -> AsyncIterator[list[Event]]:
        """
        Using the existing subscriptions, pulls greeks or quotes and yield returns them.
        Never exits unless there's an error or the channel is closed.
        """
        while True:
            message = await self._queue.get()
            logger.debug('popped message: %s', message)
            yield _map_message(message)

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
            await self.websocket.send(json.dumps([message]))
            # send the heartbeat every 10 seconds
            await asyncio.sleep(10)

    async def subscribe(self, key: EventType, dxfeeds: list[str]) -> None:
        """
        Subscribes to quotes for given list of symbols. Used for recurring data feeds;
        if you just want to get a one-time quote, use :meth:`stream`.

        :param key: type of subscription to add
        :param dxfeeds: list of symbols to subscribe for
        """
        id = await self._next_id()
        message = {
            'id': id,
            'channel': Channel.SUBSCRIPTION,
            'data': {
                'reset': True,
                'add': {key: dxfeeds}
            },
            'clientId': self.client_id
        }
        logger.debug('sending subscription: %s', message)
        await self.websocket.send(json.dumps([message]))

    async def unsubscribe(self, key: EventType, dxfeeds: list[str]) -> None:
        """
        Removes existing subscription for given list of symbols.

        :param key: type of subscription to remove
        :param dxfeeds: list of symbols to unsubscribe from
        """
        id = await self._next_id()
        message = {
            'id': id,
            'channel': Channel.SUBSCRIPTION,
            'clientId': self.client_id,
            'data': {
                'reset': True,
                'remove': {key: dxfeeds}
            }
        }
        logger.debug('sending unsubscription: %s', message)
        await self.websocket.send(json.dumps([message]))

    async def stream(self, key: EventType, dxfeeds: list[str]) -> list[Event]:
        """
        Using the given information, subscribes to the list of symbols passed, streams
        the requested information once, then unsubscribes. If you want to maintain the
        subscription open, add a subscription with :meth:`subscribe` and listen with
        :meth:`listen`.

        :param key: the type of subscription to stream, either greeks or quotes
        :param dxfeeds: list of symbols to subscribe to

        :return: list of :class:`~tastytrade.dxfeed.event.Event`s pulled.
        """
        await self.subscribe(key, dxfeeds)
        data = []
        async for item in self.listen():
            data.extend(item)
            if len(data) >= len(dxfeeds):
                break
        await self.unsubscribe(key, dxfeeds)
        return data


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
    if msg_type == EventType.GREEKS:
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
