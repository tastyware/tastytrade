from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Optional

import requests

from tastytrade.session import Session
from tastytrade.utils import validate_response


@dataclass
class Account:
    account_number: str
    opened_at: datetime
    nickname: str
    account_type_name: str
    is_closed: bool
    day_trader_status: Optional[str] = None
    closed_at: Optional[str] = None
    is_firm_error: Optional[bool] = None
    is_firm_proprietary: Optional[bool] = None
    is_futures_approved: Optional[bool] = None
    is_test_drive: Optional[str] = None
    margin_or_cash: Optional[str] = None
    is_foreign: Optional[str] = None
    funding_date: Optional[date] = None
    investment_objective: Optional[str] = None
    liquidity_needs: Optional[str] = None
    risk_tolerance: Optional[str] = None
    investment_time_horizon: Optional[str] = None
    futures_account_purpose: Optional[str] = None
    external_fdid: Optional[str] = None
    suitable_options_level: Optional[str] = None
    created_at: Optional[datetime] = None
    submitting_user_id: Optional[str] = None

    def __init__(self, json: dict[str, Any]):
        """
        Creates an Account object from the JSON returned by the Tastytrade API.
        """
        for key in json:
            snake_case = key.replace('-', '_')
            setattr(self, snake_case, json[key])

    @classmethod
    def get_accounts(cls, session: Session, include_closed=False) -> list['Account']:
        """
        Gets all trading accounts from the Tastyworks platform. By default
        excludes closed accounts from the results.

        :param session: the session to use for the request.

        :return: a list of Account objects.
        """

        response = requests.get(
            f'{session.base_url}/customers/me/accounts',
            headers=session.headers
        )
        validate_response(response)  # throws exception if not 200

        accounts = []
        data = response.json()['data']
        for entry in data['items']:
            account = entry['account']
            if not include_closed and account['is-closed']:
                continue
            accounts.append(cls(account))

        return accounts

    @classmethod
    def get_account(cls, session: Session, account_id: str) -> 'Account':
        """
        Returns a new :class:`Account` object for the given account ID.

        :param session: the session to use for the request.
        :param account_id: the account ID to get.

        :return: account corresponding to the given ID.
        """

        response = requests.get(
            f'{session.base_url}/customers/me/accounts/{account_id}',
            headers=session.headers
        )
        validate_response(response)  # throws exception if not 200

        account = response.json()['data']
        return cls(account)

    def get_trading_status(self, session: Session) -> dict[str, Any]:
        """
        Get the trading status of the account.

        :param session: the session to use for the request.
        """
        response = requests.get(
            f'{session.base_url}/accounts/{self.account_number}/trading-status',
            headers=session.headers
        )
        validate_response(response)  # throws exception if not 200

        return response.json()['data']

    def get_balances(self, session: Session) -> dict[str, Any]:
        """
        Get the current balances of the account.

        :param session: the session to use for the request.
        """
        response = requests.get(
            f'{session.base_url}/accounts/{self.account_number}/balances',
            headers=session.headers
        )
        validate_response(response)  # throws exception if not 200

        return response.json()['data']

    def get_balance_snapshots(self, session: Session, snapshot_date: Optional[date] = None,
                              time_of_day: Optional[str] = None) -> list[dict[str, Any]]:
        """
        Returns a list of two balance snapshots. The first one is the specified date,
        or, if not provided, the oldest snapshot available. The second one is the most
        recent snapshot.

        If you provide the snapshot date, you must also provide the time of day.

        :param session: the session to use for the request.
        :param snapshot_date: the date of the snapshot to get.
        :param time_of_day: the time of day of the snapshot to get, either 'EOD' or 'BOD'.
        """
        params = {
            'snapshot-date': snapshot_date,
            'time-of-day': time_of_day
        }

        response = requests.get(
            f'{session.base_url}/accounts/{self.account_number}/balance-snapshots',
            headers=session.headers,
            params={k: v for k, v in params.items() if v is not None}  # type: ignore
        )
        validate_response(response)  # throws exception if not 200

        return response.json()['data']['items']

    def get_positions(self, session: Session, underlying_symbols: Optional[list[str]] = None,
                      symbol: Optional[str] = None, instrument_type: Optional[str] = None,
                      include_closed: bool = False, underlying_product_code: Optional[str] = None,
                      partition_keys: Optional[list[str]] = None, net_positions: bool = False,
                      include_marks: bool = False) -> list[dict[str, Any]]:
        """
        Get the current positions of the account.

        :param session: the session to use for the request.
        :param underlying_symbols: an array of underlying symbols for positions.
        :param symbol: a single symbol.
        :param instrument_type:
            the type of instrument. Available values: Bond, Cryptocurrency, Currency Pair,
            Equity, Equity Offering, Equity Option, Future, Future Option, Index, Unknown, Warrant.
        :param include_closed: if closed positions should be included in the query.
        :param underlying_product_code: the underlying future's product code.
        :param partition_keys: account partition keys.
        :param net_positions: returns net positions grouped by instrument type and symbol.
        :param include_marks: include current quote mark (note: can decrease performance).
        """
        params = {
            'underlying-symbol': underlying_symbols,
            'symbol': symbol,
            'instrument-type': instrument_type,
            'include-closed-positions': include_closed,
            'underlying-product-code': underlying_product_code,
            'partition-keys': partition_keys,
            'net-positions': net_positions,
            'include-marks': include_marks
        }
        response = requests.get(
            f'{session.base_url}/accounts/{self.account_number}/positions',
            headers=session.headers,
            params={k: v for k, v in params.items() if v is not None}  # type: ignore
        )
        validate_response(response)  # throws exception if not 200

        return response.json()['data']['items']
