import datetime
import logging
from enum import Enum
from typing import Any, AsyncIterator

import aiocometd
import requests
from aiocometd import ConnectionType

from tastytrade.dxfeed import DATA_CHANNEL, SUBSCRIPTION_CHANNEL
from tastytrade.dxfeed.greeks import Greeks
from tastytrade.dxfeed.quote import Quote
from tastytrade.dxfeed.trade import Trade
from tastytrade.utils import API_URL, Session

LOGGER = logging.getLogger(__name__)
logging.getLogger('aiocometd').setLevel(logging.CRITICAL)


class SubscriptionType(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the valid subscription types for the quote streamer.
    """
    #: Used to stream options greeks (obviously only for options symbols)
    GREEKS = 'Greeks'
    #: Used to stream price quotes (for either options, ETF, futures, crypto or equity symbols)
    QUOTE = 'Quote'
    #: Used currently only for IVR
    TRADE = 'Trade'
    #: Currently unused
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

        sub = ['SPY', 'GLD']  # list of quotes to fetch
        quote = await streamer.stream(SubscriptionType.QUOTE, sub)

    """
    def __init__(self, session: Session):
        if not session.is_active():
            raise Exception('TastyWorks API session not active/valid')
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

    async def add_data_sub(self, key: SubscriptionType, dxfeeds: list[str]):
        """
        Subscribes to quotes for given list of symbols. Used for recurring data feeds; if you just want to get a one-time quote, use :meth:`stream`.

        :param key: type of subscription to add
        :param dxfeeds: list of symbols to subscribe for
        """
        streamer_dict = {key: dxfeeds}
        LOGGER.debug(f'Adding subscription: {streamer_dict}')
        await self._send_msg(SUBSCRIPTION_CHANNEL, {'add': streamer_dict})

    async def remove_data_sub(self, key: SubscriptionType, dxfeeds: list[str]):
        """
        Removes existing subscription for given list of symbols.

        :param key: type of subscription to remove
        :param dxfeeds: list of symbols to unsubscribe from
        """
        # NOTE: Experimental, unconfirmed. Needs testing
        streamer_dict = {key: dxfeeds}
        LOGGER.debug(f'Removing subscription: {streamer_dict}')
        await self._send_msg(SUBSCRIPTION_CHANNEL, {'remove': streamer_dict})

    async def _consumer(self, message):
        return _map_message(message)

    async def _send_msg(self, channel, message):
        if not self.logged_in:
            raise Exception('Connection not made or logged in')
        LOGGER.debug('[dxFeed] sending: %s on channel: %s', message, channel)
        await self.cometd_client.publish(channel, message)

    async def reset_data_subs(self):
        """
        Clears all existing subscriptions.
        """
        LOGGER.debug('Resetting data subscriptions')
        await self._send_msg(SUBSCRIPTION_CHANNEL, {'reset': True})

    def get_streamer_token(self):
        return self._get_streamer_data()['data']['token']

    def _get_streamer_data(self):
        if not self.tasty_session.logged_in:
            raise Exception('Logged in session required')

        if hasattr(self, 'streamer_data_created') and (datetime.datetime.now() - self.streamer_data_created).total_seconds() < 60:
            return self.streamer_data

        resp = requests.get(f'{API_URL}/quote-streamer-tokens', headers=self.tasty_session.get_request_headers())
        if resp.status_code != 200:
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

    async def _setup_connection(self):
        aiocometd.client.DEFAULT_CONNECTION_TYPE = ConnectionType.WEBSOCKET
        streamer_url = self._get_streamer_websocket_url()
        LOGGER.debug('Connecting to url: %s', streamer_url)

        auth_extension = AuthExtension(self.get_streamer_token())
        cometd_client = aiocometd.Client(
            streamer_url,
            auth=auth_extension,
        )
        await cometd_client.open()
        await cometd_client.subscribe(DATA_CHANNEL)

        self.cometd_client = cometd_client
        self.logged_in = True
        LOGGER.debug('Connected and logged in to dxFeed data stream')

        await self.reset_data_subs()

    async def close(self):
        """
        Closes all existing subscriptions and the cometd client. Should be called to avoid asyncio exceptions when you finish using the streamer.
        """
        await self.cometd_client.close()

    async def listen(self) -> AsyncIterator[Greeks | Quote | Trade]:
        """
        Using the existing subscriptions, pulls greeks or quotes and yield returns them. Never exits unless there's an error or the channel is closed.
        """
        async for msg in self.cometd_client:
            LOGGER.debug('[dxFeed] received: %s', msg)
            if msg['channel'] != DATA_CHANNEL:
                continue
            yield await self._consumer(msg['data'])

    async def stream(self, key: SubscriptionType, dxfeeds: list[str]) -> list[dict[str, Any]]:
        """
        Using the given information, subscribes to the list of symbols passed, streams the requested information once, then unsubscribes. If you want to maintain the subscription open, add a subscription with :meth:`add_data_sub` and listen with :meth:`listen`.

        :param key: the type of subscription to stream, either greeks or quotes
        :param dxfeeds: list of symbols to subscribe to

        :return: list of quotes or greeks pulled.
        """
        await self.add_data_sub(key, dxfeeds)
        data = []
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


def _map_message(message) -> Greeks | Quote | Trade:
    if isinstance(message[0], str):
        first_sample = False
        msg_type = message[0]
    else:
        first_sample = True
        msg_type = message[0][0]
    # regardless, the second element will be the raw data
    data = message[1]

    # parse type or warn for unknown type
    if msg_type == SubscriptionType.QUOTE:
        res = Quote.from_stream(data)
    elif msg_type == SubscriptionType.GREEKS:
        res = Greeks.from_stream(data)
    elif msg_type == SubscriptionType.TRADE:
        res = Trade.from_stream(data)
    else:
        LOGGER.warning("Unknown message type received from streamer: {}".format(message))
        res = [{'warning': 'Unknown message type received', 'message': message}]

    return res