import datetime
from enum import Enum
from typing import AsyncIterator

import aiocometd
import requests
from aiocometd import ConnectionType

from tastytrade import API_URL, log
from tastytrade.dxfeed import DATA_CHANNEL, SUBSCRIPTION_CHANNEL
from tastytrade.dxfeed.event import Event
from tastytrade.dxfeed.greeks import Greeks
from tastytrade.dxfeed.profile import Profile
from tastytrade.dxfeed.quote import Quote
from tastytrade.dxfeed.summary import Summary
from tastytrade.dxfeed.theoprice import TheoPrice
from tastytrade.dxfeed.trade import Trade
from tastytrade.session import Session


class EventType(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the valid subscription types for the quote streamer.

    Information on different types of events, their uses and their properties can be found at the `dxfeed Knowledge Base <https://kb.dxfeed.com/en/data-model/dxfeed-api-market-events.html>`_.
    """
    GREEKS = 'Greeks'
    QUOTE = 'Quote'
    TRADE = 'Trade'
    PROFILE = 'Profile'
    SUMMARY = 'Summary'
    THEO_PRICE = 'TheoPrice'


class DataStreamer:
    """
    A :class:`DataStreamer` object is used to fetch quotes or greeks for a given symbol or list of symbols. It should always be initialized using the :meth:`create` function, since the object cannot be fully instantiated without using async.

    :param session: active user session to use

    Example usage::

        session = Session('user', 'pass)
        streamer = await DataStreamer.create(session)

        subs = ['SPY', 'GLD']  # list of quotes to fetch
        quote = await streamer.stream(EventType.QUOTE, subs)

    """
    def __init__(self, session: Session):
        if not session.is_valid():
            raise Exception('Tastyworks API session not active/valid')
        #: The active session used to initiate the streamer or make requests
        self.tasty_session: Session = session
        #: The cometd client which handles requests behind the scenes
        self.cometd_client: aiocometd.Client

    @classmethod
    async def create(cls, session: Session):
        """
        async-compatible constructor for the :class:`DataStreamer` object. Simply calls the constructor and performs the asynchronous setup tasks. This should be used instead of the constructor.

        :param session: active user session to use
        """
        self = DataStreamer(session)
        await self._setup_connection()
        return self

    async def _setup_connection(self):
        aiocometd.client.DEFAULT_CONNECTION_TYPE = ConnectionType.WEBSOCKET
        streamer_url = self._get_streamer_websocket_url()
        log.debug('Connecting to url: %s', streamer_url)

        auth_extension = AuthExtension(self._get_streamer_token())
        cometd_client = aiocometd.Client(
            streamer_url,
            auth=auth_extension,
        )
        await cometd_client.open()
        await cometd_client.subscribe(DATA_CHANNEL)

        self.cometd_client = cometd_client
        self.logged_in = True
        log.debug('Connected and logged in to dxFeed data stream')

        await self.reset_data_subs()

    async def reset_data_subs(self):
        """
        Clears all existing subscriptions.
        """
        log.debug('Resetting data subscriptions')
        await self._send_msg(SUBSCRIPTION_CHANNEL, {'reset': True})

    async def add_data_sub(self, key: EventType, dxfeeds: list[str]):
        """
        Subscribes to quotes for given list of symbols. Used for recurring data feeds; if you just want to get a one-time quote, use :meth:`stream`.

        :param key: type of subscription to add
        :param dxfeeds: list of symbols to subscribe for
        """
        streamer_dict = {key: dxfeeds}
        log.debug(f'Adding subscription: {streamer_dict}')
        await self._send_msg(SUBSCRIPTION_CHANNEL, {'add': streamer_dict})

    async def remove_data_sub(self, key: EventType, dxfeeds: list[str]):
        """
        Removes existing subscription for given list of symbols.

        :param key: type of subscription to remove
        :param dxfeeds: list of symbols to unsubscribe from
        """
        streamer_dict = {key: dxfeeds}
        log.debug(f'Removing subscription: {streamer_dict}')
        await self._send_msg(SUBSCRIPTION_CHANNEL, {'remove': streamer_dict})

    async def _send_msg(self, channel, message):
        log.debug('[dxFeed] sending: %s on channel: %s', message, channel)
        await self.cometd_client.publish(channel, message)

    def _get_streamer_token(self):
        return self._get_streamer_data()['data']['token']

    def _get_streamer_data(self):
        if hasattr(self, 'streamer_data_created') and (datetime.datetime.now() - self.streamer_data_created).total_seconds() < 60:
            return self.streamer_data

        resp = requests.get(f'{API_URL}/quote-streamer-tokens', headers=self.tasty_session.get_request_headers())
        if resp.status_code // 100 != 2:
            raise Exception('Could not get quote streamer data, error message: {}'.format(
                resp.json()['error']['message']
            ))
        self.streamer_data = resp.json()
        self.streamer_data_created = datetime.datetime.now()
        return resp.json()

    def _get_streamer_websocket_url(self):
        socket_url = self._get_streamer_data()['data']['websocket-url']
        full_url = '{}/cometd'.format(socket_url)
        return full_url

    async def close(self):
        """
        Closes all existing subscriptions and the cometd client. Should be called to avoid asyncio exceptions when you finish using the streamer.
        """
        await self.cometd_client.close()

    async def listen(self) -> AsyncIterator[list[Event]]:
        """
        Using the existing subscriptions, pulls greeks or quotes and yield returns them. Never exits unless there's an error or the channel is closed.
        """
        async for msg in self.cometd_client:
            log.debug('[dxFeed] received: %s', msg)
            if msg['channel'] != DATA_CHANNEL:
                continue
            yield _map_message(msg['data'])

    async def stream(self, key: EventType, dxfeeds: list[str]) -> list[Event]:
        """
        Using the given information, subscribes to the list of symbols passed, streams the requested information once, then unsubscribes. If you want to maintain the subscription open, add a subscription with :meth:`add_data_sub` and listen with :meth:`listen`.

        :param key: the type of subscription to stream, either greeks or quotes
        :param dxfeeds: list of symbols to subscribe to

        :return: list of quotes or greeks pulled.
        """
        await self.add_data_sub(key, dxfeeds)
        data: list[Event] = []
        async for item in self.listen():
            data.extend(item)
            if len(data) >= len(dxfeeds):
                break
        await self.remove_data_sub(key, dxfeeds)
        return data


class AuthExtension(aiocometd.AuthExtension):
    def __init__(self, streamer_token: str):
        self.streamer_token = streamer_token

    def _get_login_msg(self):
        return {'ext': {'com.devexperts.auth.AuthToken': f'{self.streamer_token}'}}

    def _get_advice_msg(self):
        return {
            'timeout': 60 * 1000,
            'interval': 0
        }

    async def incoming(self, payload, headers=None):
        pass

    async def outgoing(self, payload, headers=None):
        for entry in payload:
            if 'clientId' not in entry:
                entry.update(self._get_login_msg())

    async def authenticate(self):
        pass


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
        raise Exception("Unknown message type received from streamer: {}".format(message))

    return res
