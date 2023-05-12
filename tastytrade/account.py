from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Optional

import requests

from tastytrade.session import Session
from tastytrade.utils import TastytradeError, validate_response


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
        Creates an Account object from the Tastytrade 'Account' object in JSON format.
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

        :return: a list of :class:`Account` objects.
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

        :return: :class:`Account` object corresponding to the given ID.
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

        :return: a Tastytrade 'TradingStatus' object in JSON format.
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

        :return: a Tastytrade 'AccountBalance' object in JSON format.
        """
        response = requests.get(
            f'{session.base_url}/accounts/{self.account_number}/balances',
            headers=session.headers
        )
        validate_response(response)  # throws exception if not 200

        return response.json()['data']

    def get_balance_snapshots(
        self,
        session: Session,
        snapshot_date: Optional[date] = None,
        time_of_day: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """
        Returns a list of two balance snapshots. The first one is the specified date,
        or, if not provided, the oldest snapshot available. The second one is the most
        recent snapshot.

        If you provide the snapshot date, you must also provide the time of day.

        :param session: the session to use for the request.
        :param snapshot_date: the date of the snapshot to get.
        :param time_of_day: the time of day of the snapshot to get, either 'EOD' or 'BOD'.

        :return: a list of two Tastytrade 'AccountBalanceSnapshot' objects in JSON format.
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

    def get_positions(
        self,
        session: Session,
        underlying_symbols: Optional[list[str]] = None,
        symbol: Optional[str] = None,
        instrument_type: Optional[str] = None,
        include_closed: bool = False,
        underlying_product_code: Optional[str] = None,
        partition_keys: Optional[list[str]] = None,
        net_positions: bool = False,
        include_marks: bool = False
    ) -> list[dict[str, Any]]:
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

        :return: a list of Tastytrade 'CurrentPosition' objects in JSON format.
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

    def get_history(
        self,
        session: Session,
        per_page: int = 250,
        page_offset: Optional[int] = None,
        sort: str = 'Desc',
        type: Optional[str] = None,
        sub_types: Optional[list[str]] = None,
        start_date: Optional[date] = None,
        end_date: date = date.today(),
        instrument_type: Optional[str] = None,
        symbol: Optional[str] = None,
        underlying_symbol: Optional[str] = None,
        action: Optional[str] = None,
        partition_key: Optional[str] = None,
        futures_symbol: Optional[str] = None,
        start_at: Optional[datetime] = None,
        end_at: Optional[datetime] = None
    ) -> list[dict[str, Any]]:
        """
        Get transaction history of the account.

        :param session: the session to use for the request.
        :param per_page: the number of transactions to return per page.
        :param page_offset: the page to fetch. Use this if you only want a specific page.
        :param sort: the order to sort results in, either 'Desc' or 'Asc'.
        :param type: the type of transaction.
        :param sub_types: an array of transaction subtypes to filter by.
        :param start_date: the start date of transactions to query.
        :param end_date: the end date of transactions to query.
        :param instrument_type:
            the type of instrument, i.e. Bond, Cryptocurrency, Equity, Equity Offering,
            Equity Option, Future, Future Option, Index, Unknown or Warrant.
        :param symbol: a single symbol.
        :param underlying_symbol: the underlying symbol.
        :param action:
            the action of the transaction: 'Sell to Open', 'Sell to Close', 'Buy to Open',
            'Buy to Close', 'Sell' or 'Buy'.
        :param partition_key: account partition key.
        :param futures_symbol: the full TW Future Symbol, e.g. /ESZ9, /NGZ19.
        :param start_at: datetime start range for filtering transactions in full date-time.
        :param end_at: datetime end range for filtering transactions in full date-time.

        :return: a list of Tastytrade 'Transaction' objects in JSON format.
        """
        params = {
            'per-page': per_page,
            'page-offset': page_offset,
            'sort': sort,
            'type': type,
            'sub-type': sub_types,
            'start-date': start_date,
            'end-date': end_date,
            'instrument-type': instrument_type,
            'symbol': symbol,
            'underlying-symbol': underlying_symbol,
            'action': action,
            'partition-key': partition_key,
            'futures-symbol': futures_symbol,
            'start-at': start_at,
            'end-at': end_at
        }
        # if page offset is specified, only get that page
        if params['page-offset']:
            is_paged = False
        # if page offset is not specified, get all pages
        else:
            is_paged = True
            params['page-offset'] = 0

        # loop through pages and get all transactions
        results = []
        while True:
            response = requests.get(
                f'{session.base_url}/accounts/{self.account_number}/transactions',
                headers=session.headers,
                params={k: v for k, v in params.items() if v is not None}  # type: ignore
            )
            validate_response(response)

            data = response.json()
            results.extend(data['data']['items'])

            if not is_paged:
                break

            pagination = data['pagination']
            if pagination['page-offset'] >= pagination['total-pages'] - 1:
                break
            params['page-offset'] += 1  # type: ignore

        return results

    def get_transaction(self, session: Session, id: int) -> dict[str, Any]:
        """
        Get a single transaction by ID.

        :param session: the session to use for the request.
        :param id: the ID of the transaction to fetch.

        :return: a Tastytrade 'Transaction' object in JSON format.
        """
        response = requests.get(
            f'{session.base_url}/accounts/{self.account_number}/transactions/{id}',
            headers=session.headers
        )
        validate_response(response)

        return response.json()['data']

    def get_total_fees(self, session: Session, date: date = date.today()) -> dict[str, Any]:
        """
        Get the total fees for a given date.

        :param session: the session to use for the request.
        :param date: the date to get fees for.

        :return: a dict containing the total fees and the price effect.
        """
        params = {'date': date}
        response = requests.get(
            f'{session.base_url}/accounts/{self.account_number}/transactions/total-fees',
            headers=session.headers,
            params=params  # type: ignore
        )
        validate_response(response)

        return response.json()['data']

    def get_net_liquidating_value_history(
        self,
        session: Session,
        time_back: Optional[str] = None,
        start_time: Optional[datetime] = None
    ) -> list[dict[str, Any]]:
        """
        Returns a list of account net liquidating value snapshots over the specified time period.

        :param session: the session to use for the request.
        :param time_back:
            the time period to get net liquidating value snapshots for. This param is required
            if start_time is not given. Possible values are: '1d', '1m', '3m', '6m', '1y', 'all'.
        :param start_time:
            the start point for the query. This param is required is time-back is not given.
            If given, will take precedence over time-back.

        :return: a list of Tastytrade 'NetLiqOhlc' objects in JSON format.
        """
        params: dict[str, Any] = {}
        if start_time:
            # format to Tastytrade DateTime format
            start_time = str(start_time).replace(' ', 'T').split('.')[0] + 'Z'  # type: ignore
            params = {'start-time': start_time}
        elif not time_back:
            raise TastytradeError('Either time_back or start_time must be specified.')
        else:
            params = {'time-back': time_back}

        response = requests.get(
            f'{session.base_url}/accounts/{self.account_number}/net-liq/history',
            headers=session.headers,
            params=params
        )
        validate_response(response)

        return response.json()['data']['items']

    def get_position_limit(self, session: Session) -> dict[str, Any]:
        """
        Get the maximum order size information for the account.

        :param session: the session to use for the request.

        :return: a Tastytrade 'PositionLimit' object in JSON format.
        """
        response = requests.get(
            f'{session.base_url}/accounts/{self.account_number}/position-limit',
            headers=session.headers
        )
        validate_response(response)

        return response.json()['data']

    def get_effective_margin_requirements(self, session: Session, symbol: str) -> dict[str, Any]:
        """
        Get the effective margin requirements for a given symbol.

        :param session: the session to use for the request.
        :param symbol: the symbol to get margin requirements for.

        :return: a Tastytrade 'MarginRequirement' object in JSON format.
        """
        response = requests.get(
            f'{session.base_url}/accounts/{self.account_number}/margin-requirements/{symbol}/effective',
            headers=session.headers
        )
        validate_response(response)

        return response.json()['data']
