from dataclasses import dataclass
from typing import List

import aiohttp

from tastyworks.models.order import Order, OrderPriceEffect


@dataclass
class TradingAccount(object):
    account_number: str
    external_id: str
    is_margin: bool
    is_closed: bool
    account_type_name: str
    nickname: str
    opened_at: str

    async def execute_order(self, order: Order, session, dry_run=True):
        """
        Execute an order. If doing a dry run, the order isn't placed but simulated (server-side).

        Args:
            order (Order): The order object to execute.
            session (TastyAPISession): The tastyworks session onto which to execute the order.
            dry_run (bool): Whether to do a test (dry) run.

        Returns:
            bool: Whether the order was successful.
        """
        if not order.check_is_order_executable():
            raise Exception('Order is not executable, most likely due to missing data')

        if not session.is_active():
            raise Exception('The supplied session is not active and valid')

        url = '{}/accounts/{}/orders'.format(
            session.API_url,
            self.account_number
        )
        if dry_run:
            url = f'{url}/dry-run'

        body = _get_execute_order_json(order)

        async with aiohttp.request('POST', url, headers=session.get_request_headers(), json=body) as resp:
            if resp.status == 201:
                return (await resp.json())['data']
            elif resp.status == 400:
                raise Exception('Order execution failed: {}'.format(await resp.text()))
            else:
                raise Exception('Unknown remote error {}: {}'.format(resp.status, await resp.text()))

    @classmethod
    def from_dict(cls, data: dict) -> List:
        """
        Parses a TradingAccount object from a dict.
        """
        new_data = {
            'is_margin': True if data['margin-or-cash'] == 'Margin' else False,
            'account_number': data['account-number'],
            'external_id': data['external-id'],
            'is_closed': True if data['is-closed'] else False,
            'account_type_name': data['account-type-name'],
            'nickname': data['nickname'],
            'opened_at': data['opened-at']
        }

        res = TradingAccount(**new_data)

        return res

    @classmethod
    async def get_remote_accounts(cls, session) -> List:
        """
        Gets all trading accounts from the Tastyworks platform.

        Args:
            session (TastyAPISession): An active and logged-in session object against which to query.

        Returns:
            list (TradingAccount): A list of trading accounts.
        """
        url = f'{session.API_url}/customers/me/accounts'
        res = []

        async with aiohttp.request('GET', url, headers=session.get_request_headers()) as response:
            if response.status != 200:
                raise Exception('Could not get trading accounts info from Tastyworks...')
            data = (await response.json())['data']

        for entry in data['items']:
            if entry['authority-level'] != 'owner':
                continue
            acct_data = entry['account']
            acct = TradingAccount.from_dict(acct_data)
            res.append(acct)

        return res

    async def get_balance(self, session, **kwargs):
        """
        Get balance.

        Args:
            session (TastyAPISession): An active and logged-in session object against which to query.
        Returns:
            dict: account attributes
        """
        url = '{}/accounts/{}/balances'.format(
            session.API_url,
            self.account_number
        )

        async with aiohttp.request('GET', url, headers=session.get_request_headers(), **kwargs) as response:
            if response.status != 200:
                raise Exception('Could not get trading account balance info from Tastyworks...')
            data = (await response.json())['data']
        return data

    async def get_positions(self, session, **kwargs):
        """
        Get Open Positions.

        Args:
            session (TastyAPISession): An active and logged-in session object against which to query.
        Returns:
            dict: account attributes
        """
        url = '{}/accounts/{}/positions'.format(
            session.API_url,
            self.account_number
        )

        async with aiohttp.request('GET', url, headers=session.get_request_headers(), **kwargs) as response:
            if response.status != 200:
                raise Exception('Could not get open positions info from Tastyworks...')
            data = (await response.json())['data']['items']
        return data

    async def get_live_orders(self, session, **kwargs):
        """
        Get live Orders.

        Args:
            session (TastyAPISession): An active and logged-in session object against which to query.
        Returns:
            dict: account attributes
        """
        url = '{}/accounts/{}/orders/live'.format(
            session.API_url,
            self.account_number
        )

        async with aiohttp.request('GET', url, headers=session.get_request_headers(), **kwargs) as response:
            if response.status != 200:
                raise Exception('Could not get live orders info from Tastyworks...')
            data = (await response.json())['data']['items']
        return data

    async def get_history(self, session, **kwargs):
        """
        Get transaction history.

        Args:
            session (TastyAPISession): An active and logged-in session object against which to query.
        Returns:
            dict: account attributes
        """
        url = '{}/accounts/{}/transactions'.format(
            session.API_url,
            self.account_number
        )

        PAGE_SIZE = 1024

        page_offset = 0
        total_pages = None
        total_items = 0
        all_items = []

        while total_pages is None or page_offset < total_pages:
            # print(f'Getting page {page_offset}')
            params = kwargs.pop('params', {})
            params.update({
                'per-page': PAGE_SIZE,
                'page-offset': page_offset,
            })
            kwargs['params'] = params

            async with aiohttp.request('GET', url, headers=session.get_request_headers(), **kwargs) as response:
                if response.status != 200:
                    raise Exception('Could not get history info from Tastyworks...')
                data = (await response.json())

            page_offset += 1
            if total_pages is None:
                pagination = data['pagination']
                total_pages = pagination['total-pages']
                total_items = pagination['total-items']

            items = data['data']['items']
            if items:
                all_items.extend(items)

        if len(all_items) != total_items:
            raise Exception('Could not fetch some items in paginated request.')

        return all_items


def _get_execute_order_json(order: Order):
    order_json = {
        'source': order.details.source,
        'order-type': order.details.type.value,
        'price': '{:.2f}'.format(order.details.price),
        'price-effect': order.details.price_effect.value,
        'time-in-force': order.details.time_in_force.value,
        'legs': _get_legs_request_data(order)
    }

    if order.details.gtc_date:
        order_json['gtc-date'] = order.details.gtc_date.strftime('%Y-%m-%d')

    return order_json


def _get_legs_request_data(order):
    res = []
    order_effect = order.details.price_effect
    order_effect_str = 'Sell to Open' if order_effect == OrderPriceEffect.CREDIT else 'Buy to Open'
    for leg in order.details.legs:
        leg_dict = {**leg.to_tasty_json(), 'action': order_effect_str}
        res.append(leg_dict)
    return res
