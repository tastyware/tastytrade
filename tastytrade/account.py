from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional, TypedDict

import requests

from tastytrade.session import Session
from tastytrade.utils import (TastytradeError, datetime_from_tastydatetime,
                              snakeify, validate_response)

AccountBalance = TypedDict('AccountBalance', {
    'account-number': str,
    'cash-balance': Decimal,
    'long-equity-value': Decimal,
    'short-equity-value': Decimal,
    'long-derivative-value': Decimal,
    'short-derivative-value': Decimal,
    'long-futures-value': Decimal,
    'short-futures-value': Decimal,
    'long-futures-derivative-value': Decimal,
    'short-futures-derivative-value': Decimal,
    'long-margineable-value': Decimal,
    'short-margineable-value': Decimal,
    'margin-equity': Decimal,
    'equity-buying-power': Decimal,
    'derivative-buying-power': Decimal,
    'day-trading-buying-power': Decimal,
    'futures-margin-requirement': Decimal,
    'available-trading-funds': Decimal,
    'maintenance-requirement': Decimal,
    'maintenance-call-value': Decimal,
    'reg-t-call-value': Decimal,
    'day-trading-call-value': Decimal,
    'day-equity-call-value': Decimal,
    'net-liquidating-value': Decimal,
    'cash-available-to-withdraw': Decimal,
    'day-trade-excess': Decimal,
    'pending-cash': Decimal,
    'pending-cash-effect': str,
    'long-cryptocurrency-value': Decimal,
    'short-cryptocurrency-value': Decimal,
    'cryptocurrency-margin-requirement': Decimal,
    'unsettled-cryptocurrency-fiat-amount': Decimal,
    'unsettled-cryptocurrency-fiat-effect': str,
    'closed-loop-available-balance': Decimal,
    'equity-offering-margin-requirement': Decimal,
    'long-bond-value': Decimal,
    'bond-margin-requirement': Decimal,
    'snapshot-date': date,
    'time-of-day': str,
    'reg-t-margin-requirement': Decimal,
    'futures-overnight-margin-requirement': Decimal,
    'futures-intraday-margin-requirement': Decimal,
    'maintenance-excess': Decimal,
    'pending-margin-interest': Decimal,
    'apex-starting-day-margin-equity': Decimal,
    'buying-power-adjustment': Decimal,
    'buying-power-adjustment-effect': str,
    'effective-cryptocurrency-buying-power': Decimal,
    'updated-at': datetime
}, total=False)
AccountBalanceSnapshot = TypedDict('AccountBalanceSnapshot', {
    'account-number': str,
    'cash-balance': Decimal,
    'long-equity-value': Decimal,
    'short-equity-value': Decimal,
    'long-derivative-value': Decimal,
    'short-derivative-value': Decimal,
    'long-futures-value': Decimal,
    'short-futures-value': Decimal,
    'long-futures-derivative-value': Decimal,
    'short-futures-derivative-value': Decimal,
    'long-margineable-value': Decimal,
    'short-margineable-value': Decimal,
    'margin-equity': Decimal,
    'equity-buying-power': Decimal,
    'derivative-buying-power': Decimal,
    'day-trading-buying-power': Decimal,
    'futures-margin-requirement': Decimal,
    'available-trading-funds': Decimal,
    'maintenance-requirement': Decimal,
    'maintenance-call-value': Decimal,
    'reg-t-call-value': Decimal,
    'day-trading-call-value': Decimal,
    'day-equity-call-value': Decimal,
    'net-liquidating-value': Decimal,
    'cash-available-to-withdraw': Decimal,
    'day-trade-excess': Decimal,
    'pending-cash': Decimal,
    'pending-cash-effect': str,
    'long-cryptocurrency-value': Decimal,
    'short-cryptocurrency-value': Decimal,
    'cryptocurrency-margin-requirement': Decimal,
    'unsettled-cryptocurrency-fiat-amount': Decimal,
    'unsettled-cryptocurrency-fiat-effect': str,
    'closed-loop-available-balance': Decimal,
    'equity-offering-margin-requirement': Decimal,
    'long-bond-value': Decimal,
    'bond-margin-requirement': Decimal,
    'snapshot-date': date,
    'time-of-day': str
}, total=False)
CurrentPosition = TypedDict('CurrentPosition', {
    'account-number': str,
    'symbol': str,
    'instrument-type': str,
    'underlying-symbol': str,
    'quantity': dict,
    'quantity-direction': str,
    'close-price': Decimal,
    'average-open-price': Decimal,
    'average-yearly-market-close-price': Decimal,
    'average-daily-market-close-price': Decimal,
    'mark': Decimal,
    'mark-price': Decimal,
    'multiplier': int,
    'cost-effect': str,
    'is-suppressed': bool,
    'is-frozen': bool,
    'restricted-quantity': dict,
    'expires-at': datetime,
    'fixing-price': Decimal,
    'deliverable-type': str,
    'realized-day-gain': Decimal,
    'realized-day-gain-effect': str,
    'realized-day-gain-date': date,
    'realized-today': Decimal,
    'realized-today-effect': str,
    'realized-today-date': date,
    'created-at': datetime,
    'updated-at': datetime
}, total=False)
MarginRequirement = TypedDict('MarginRequirement', {
    'underlying-symbol': str,
    'long-equity-initial': Decimal,
    'short-equity-initial': Decimal,
    'long-equity-maintenance': Decimal,
    'short-equity-maintenance': Decimal,
    'naked-option-standard': Decimal,
    'naked-option-minimum': Decimal,
    'naked-option-floor': Decimal,
    'clearing-identifier': str,
    'is-deleted': bool
}, total=False)
NetLiqOhlc = TypedDict('NetLiqOhlc', {
    'open': Decimal,
    'high': Decimal,
    'low': Decimal,
    'close': Decimal,
    'pending-cash-open': Decimal,
    'pending-cash-high': Decimal,
    'pending-cash-low': Decimal,
    'pending-cash-close': Decimal,
    'total-open': Decimal,
    'total-high': Decimal,
    'total-low': Decimal,
    'total-close': Decimal,
    'time': datetime
}, total=False)
PositionLimit = TypedDict('PositionLimit', {
    'id': int,
    'account-number': str,
    'equity-order-size': int,
    'equity-option-order-size': int,
    'future-order-size': int,
    'future-option-order-size': int,
    'underlying-opening-order-limit': int,
    'equity-position-size': int,
    'equity-option-position-size': int,
    'future-position-size': int,
    'future-option-position-size': int
}, total=False)
Transaction = TypedDict('Transaction', {
    'id': int,
    'account-number': str,
    'symbol': str,
    'instrument-type': str,
    'underlying-symbol': str,
    'transaction-type': str,
    'transaction-sub-type': str,
    'description': str,
    'action': str,
    'quantity': Decimal,
    'price': Decimal,
    'executed-at': datetime,
    'transaction-date': date,
    'value': Decimal,
    'value-effect': str,
    'regulatory-fees': Decimal,
    'regulatory-fees-effect': str,
    'clearing-fees': Decimal,
    'clearing-fees-effect': str,
    'other-charge': Decimal,
    'other-charge-effect': str,
    'other-charge-description': str,
    'net-value': Decimal,
    'net-value-effect': str,
    'commission': Decimal,
    'commission-effect': str,
    'proprietary-index-option-fees': Decimal,
    'proprietary-index-option-fees-effect': str,
    'is-estimated-fee': bool,
    'ext-exchange-order-number': str,
    'ext-global-order-number': int,
    'ext-group-id': str,
    'ext-group-fill-id': str,
    'ext-exec-id': str,
    'exec-id': str,
    'exchange': str,
    'order-id': int,
    'reverses-id': int,
    'exchange-affiliation-identifier': str,
    'cost-basis-reconciliation-date': date,
    'lots': list[dict[str, Any]],
    'leg-count': int,
    'destination-venue': str,
    'agency-price': Decimal,
    'principal-price': Decimal
}, total=False)
TradingStatus = TypedDict('TradingStatus', {
    'account-number': str,
    'autotrade-account-type': str,
    'clearing-account-number': str,
    'clearing-aggregation-identifier': str,
    'day-trade-count': int,
    'equities-margin-calculation-type': str,
    'fee-schedule-name': str,
    'futures-margin-rate-multiplier': Decimal,
    'has-intraday-equities-margin': bool,
    'id': int,
    'is-aggregated-at-clearing': bool,
    'is-closed': bool,
    'is-closing-only': bool,
    'is-cryptocurrency-closing-only': bool,
    'is-cryptocurrency-enabled': bool,
    'is-frozen': bool,
    'is-full-equity-margin-required': bool,
    'is-futures-closing-only': bool,
    'is-futures-intra-day-enabled': bool,
    'is-futures-enabled': bool,
    'is-in-day-trade-equity-maintenance-call': bool,
    'is-in-margin-call': bool,
    'is-pattern-day-trader': bool,
    'is-portfolio-margin-enabled': bool,
    'is-risk-reducing-only': bool,
    'is-small-notional-futures-intra-day-enabled': bool,
    'is-roll-the-day-forward-enabled': bool,
    'are-far-otm-net-options-restricted': bool,
    'options-level': str,
    'pdt-reset-on': date,
    'short-calls-enabled': bool,
    'small-notional-futures-margin-rate-multiplier': Decimal,
    'cmta-override': int,
    'is-equity-offering-enabled': bool,
    'is-equity-offering-closing-only': bool,
    'enhanced-fraud-safeguards-enabled-at': datetime,
    'updated-at': datetime
}, total=False)


@dataclass
class Account:
    account_number: str
    opened_at: datetime
    nickname: str
    account_type_name: str
    is_closed: bool
    day_trader_status: str
    is_firm_error: bool
    is_firm_proprietary: bool
    is_futures_approved: bool
    is_test_drive: bool
    margin_or_cash: str
    is_foreign: bool
    created_at: datetime
    external_id: Optional[str] = None
    closed_at: Optional[str] = None
    funding_date: Optional[date] = None
    investment_objective: Optional[str] = None
    liquidity_needs: Optional[str] = None
    risk_tolerance: Optional[str] = None
    investment_time_horizon: Optional[str] = None
    futures_account_purpose: Optional[str] = None
    external_fdid: Optional[str] = None
    suitable_options_level: Optional[str] = None
    submitting_user_id: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.opened_at, str):
            self.opened_at = datetime_from_tastydatetime(self.opened_at)
        if isinstance(self.created_at, str):
            self.created_at = datetime_from_tastydatetime(self.created_at)
        if isinstance(self.funding_date, str):
            self.funding_date = date.fromisoformat(self.funding_date)

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
        data = response.json()['data']['items']
        for entry in data:
            account = entry['account']
            if not include_closed and account['is-closed']:
                continue
            accounts.append(cls(**snakeify(account)))

        return accounts

    @classmethod
    def get_account(cls, session: Session, account_number: str) -> 'Account':
        """
        Returns a new :class:`Account` object for the given account ID.

        :param session: the session to use for the request.
        :param account_number: the account ID to get.

        :return: :class:`Account` object corresponding to the given ID.
        """
        response = requests.get(
            f'{session.base_url}/customers/me/accounts/{account_number}',
            headers=session.headers
        )
        validate_response(response)  # throws exception if not 200

        account = response.json()['data']
        return cls(**snakeify(account))

    def get_trading_status(self, session: Session) -> TradingStatus:
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

    def get_balances(self, session: Session) -> AccountBalance:
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
    ) -> list[AccountBalanceSnapshot]:
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
        params: dict[str, Any] = {
            'snapshot-date': snapshot_date,
            'time-of-day': time_of_day
        }

        response = requests.get(
            f'{session.base_url}/accounts/{self.account_number}/balance-snapshots',
            headers=session.headers,
            params={k: v for k, v in params.items() if v is not None}
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
    ) -> list[CurrentPosition]:
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
        params: dict[str, Any] = {
            'underlying-symbol[]': underlying_symbols,
            'symbol': symbol,
            'instrument-type': instrument_type,
            'include-closed-positions': include_closed,
            'underlying-product-code': underlying_product_code,
            'partition-keys[]': partition_keys,
            'net-positions': net_positions,
            'include-marks': include_marks
        }
        response = requests.get(
            f'{session.base_url}/accounts/{self.account_number}/positions',
            headers=session.headers,
            params={k: v for k, v in params.items() if v is not None}
        )
        validate_response(response)  # throws exception if not 200

        return response.json()['data']['items']

    def get_history(
        self,
        session: Session,
        per_page: int = 250,
        page_offset: int = 0,
        sort: str = 'Desc',
        type: Optional[str] = None,
        types: Optional[list[str]] = None,
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
    ) -> list[Transaction]:
        """
        Get transaction history of the account.

        :param session: the session to use for the request.
        :param per_page: the number of results to return per page.
        :param page_offset: the page offset to use.
        :param sort: the order to sort results in, either 'Desc' or 'Asc'.
        :param type: the type of transaction.
        :param types: a list of transaction types to filter by.
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
        params: dict[str, Any] = {
            'per-page': per_page,
            'page-offset': page_offset,
            'sort': sort,
            'type': type,
            'types[]': types,
            'sub-type[]': sub_types,
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

        # loop through pages and get all transactions
        results = []
        while True:
            response = requests.get(
                f'{session.base_url}/accounts/{self.account_number}/transactions',
                headers=session.headers,
                params={k: v for k, v in params.items() if v is not None}
            )
            validate_response(response)

            json = response.json()
            results.extend(json['data']['items'])

            pagination = json['pagination']
            if pagination['page-offset'] >= pagination['total-pages'] - 1:
                break
            params['page-offset'] += 1  # type: ignore

        return results

    def get_transaction(self, session: Session, id: int) -> Transaction:
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
        params: dict[str, Any] = {'date': date}
        response = requests.get(
            f'{session.base_url}/accounts/{self.account_number}/transactions/total-fees',
            headers=session.headers,
            params=params
        )
        validate_response(response)

        return response.json()['data']

    def get_net_liquidating_value_history(
        self,
        session: Session,
        time_back: Optional[str] = None,
        start_time: Optional[datetime] = None
    ) -> list[NetLiqOhlc]:
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

    def get_position_limit(self, session: Session) -> PositionLimit:
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

    def get_effective_margin_requirements(self, session: Session, symbol: str) -> MarginRequirement:
        """
        Get the effective margin requirements for a given symbol.

        :param session: the session to use for the request.
        :param symbol: the symbol to get margin requirements for.

        :return: a Tastytrade 'MarginRequirement' object in JSON format.
        """
        if symbol:
            symbol = symbol.replace('/', '%2F')
        response = requests.get(
            f'{session.base_url}/accounts/{self.account_number}/margin-requirements/{symbol}/effective',
            headers=session.headers
        )
        validate_response(response)

        return response.json()['data']

    def get_margin_requirements(self, session: Session) -> dict[str, Any]:
        """
        Get the margin requirements for the account.

        :param session: the session to use for the request.

        :return: Tastytrade margin requirements summary JSON.
        """
        response = requests.get(
            f'{session.base_url}/margin/accounts/{self.account_number}/requirements',
            headers=session.headers
        )
        validate_response(response)

        return response.json()['data']
