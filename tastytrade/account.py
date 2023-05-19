from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional, TypedDict

import requests

from tastytrade.session import Session
from tastytrade.utils import TastytradeError, TastytradeJsonDataclass, validate_response


class AccountBalance(TastytradeJsonDataclass):
    account_number: str
    cash_balance: Decimal
    long_equity_value: Decimal
    short_equity_value: Decimal
    long_derivative_value: Decimal
    short_derivative_value: Decimal
    long_futures_value: Decimal
    short_futures_value: Decimal
    long_futures_derivative_value: Decimal
    short_futures_derivative_value: Decimal
    long_margineable_value: Decimal
    short_margineable_value: Decimal
    margin_equity: Decimal
    equity_buying_power: Decimal
    derivative_buying_power: Decimal
    day_trading_buying_power: Decimal
    futures_margin_requirement: Decimal
    available_trading_funds: Decimal
    maintenance_requirement: Decimal
    maintenance_call_value: Decimal
    reg_t_call_value: Decimal
    day_trading_call_value: Decimal
    day_equity_call_value: Decimal
    net_liquidating_value: Decimal
    cash_available_to_withdraw: Decimal
    day_trade_excess: Decimal
    pending_cash: Decimal
    pending_cash_effect: str
    long_cryptocurrency_value: Decimal
    short_cryptocurrency_value: Decimal
    cryptocurrency_margin_requirement: Decimal
    unsettled_cryptocurrency_fiat_amount: Decimal
    unsettled_cryptocurrency_fiat_effect: str
    closed_loop_available_balance: Decimal
    equity_offering_margin_requirement: Decimal
    long_bond_value: Decimal
    bond_margin_requirement: Decimal
    snapshot_date: date
    time_of_day: str
    reg_t_margin_requirement: Decimal
    futures_overnight_margin_requirement: Decimal
    futures_intraday_margin_requirement: Decimal
    maintenance_excess: Decimal
    pending_margin_interest: Decimal
    apex_starting_day_margin_equity: Decimal
    buying_power_adjustment: Decimal
    buying_power_adjustment_effect: str
    effective_cryptocurrency_buying_power: Decimal
    updated_at: datetime


class AccountBalanceSnapshot(TastytradeJsonDataclass):
    account_number: str
    cash_balance: Decimal
    long_equity_value: Decimal
    short_equity_value: Decimal
    long_derivative_value: Decimal
    short_derivative_value: Decimal
    long_futures_value: Decimal
    short_futures_value: Decimal
    long_futures_derivative_value: Decimal
    short_futures_derivative_value: Decimal
    long_margineable_value: Decimal
    short_margineable_value: Decimal
    margin_equity: Decimal
    equity_buying_power: Decimal
    derivative_buying_power: Decimal
    day_trading_buying_power: Decimal
    futures_margin_requirement: Decimal
    available_trading_funds: Decimal
    maintenance_requirement: Decimal
    maintenance_call_value: Decimal
    reg_t_call_value: Decimal
    day_trading_call_value: Decimal
    day_equity_call_value: Decimal
    net_liquidating_value: Decimal
    cash_available_to_withdraw: Decimal
    day_trade_excess: Decimal
    pending_cash: Decimal
    pending_cash_effect: str
    long_cryptocurrency_value: Decimal
    short_cryptocurrency_value: Decimal
    cryptocurrency_margin_requirement: Decimal
    unsettled_cryptocurrency_fiat_amount: Decimal
    unsettled_cryptocurrency_fiat_effect: str
    closed_loop_available_balance: Decimal
    equity_offering_margin_requirement: Decimal
    long_bond_value: Decimal
    bond_margin_requirement: Decimal
    snapshot_date: date
    time_of_day: Optional[str] = None


class CurrentPosition(TastytradeJsonDataclass):
    account_number: str
    symbol: str
    instrument_type: str
    underlying_symbol: str
    quantity: Decimal
    quantity_direction: str
    close_price: Decimal
    average_open_price: Decimal
    average_yearly_market_close_price: Decimal
    average_daily_market_close_price: Decimal
    multiplier: int
    cost_effect: str
    is_suppressed: bool
    is_frozen: bool
    realized_day_gain: Decimal
    realized_day_gain_effect: str
    realized_day_gain_date: date
    realized_today: Decimal
    realized_today_effect: str
    realized_today_date: date
    created_at: datetime
    updated_at: datetime
    mark: Optional[Decimal] = None
    mark_price: Optional[Decimal] = None
    restricted_quantity: Optional[Decimal] = None
    expires_at: Optional[datetime] = None
    fixing_price: Optional[Decimal] = None
    deliverable_type: Optional[str] = None


class Lot(TastytradeJsonDataclass):
    id: str
    transaction_id: int
    quantity: Decimal
    price: Decimal
    quantity_direction: str
    executed_at: datetime
    transaction_date: date


class MarginReportEntry(TastytradeJsonDataclass):
    description: str
    code: str
    underlying_symbol: str
    underlying_type: str
    expected_price_range_up_percent: Decimal
    expected_price_range_down_percent: Decimal
    point_of_no_return_percent: Decimal
    margin_calculation_type: str
    margin_requirement: Decimal
    margin_requirement_effect: str
    initial_requirement: Decimal
    initial_requirement_effect: str
    maintenance_requirement: Decimal
    maintenance_requirement_effect: str
    buying_power: Decimal
    buying_power_effect: str
    groups: list[dict[str, Any]]
    price_increase_percent: Decimal
    price_decrease_percent: Decimal


class MarginReport(TastytradeJsonDataclass):
    account_number: str
    description: str
    margin_calculation_type: str
    option_level: str
    margin_requirement: Decimal
    margin_requirement_effect: str
    maintenance_requirement: Decimal
    maintenance_requirement_effect: str
    margin_equity: Decimal
    margin_equity_effect: str
    option_buying_power: Decimal
    option_buying_power_effect: str
    reg_t_margin_requirement: Decimal
    reg_t_margin_requirement_effect: str
    reg_t_option_buying_power: Decimal
    reg_t_option_buying_power_effect: str
    maintenance_excess: Decimal
    maintenance_excess_effect: str
    groups: list[MarginReportEntry]
    last_state_timestamp: int
    initial_requirement: Optional[Decimal] = None
    initial_requirement_effect: Optional[str] = None


class MarginRequirement(TastytradeJsonDataclass):
    underlying_symbol: str
    long_equity_initial: Decimal
    short_equity_initial: Decimal
    long_equity_maintenance: Decimal
    short_equity_maintenance: Decimal
    naked_option_standard: Decimal
    naked_option_minimum: Decimal
    naked_option_floor: Decimal
    clearing_identifier: Optional[str] = None
    is_deleted: Optional[bool] = None


class NetLiqOhlc(TastytradeJsonDataclass):
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    pending_cash_open: Decimal
    pending_cash_high: Decimal
    pending_cash_low: Decimal
    pending_cash_close: Decimal
    total_open: Decimal
    total_high: Decimal
    total_low: Decimal
    total_close: Decimal
    time: datetime


class PositionLimit(TastytradeJsonDataclass):
    account_number: str
    equity_order_size: int
    equity_option_order_size: int
    future_order_size: int
    future_option_order_size: int
    underlying_opening_order_limit: int
    equity_position_size: int
    equity_option_position_size: int
    future_position_size: int
    future_option_position_size: int


class TradingStatus(TastytradeJsonDataclass):
    account_number: str
    equities_margin_calculation_type: str
    fee_schedule_name: str
    futures_margin_rate_multiplier: Decimal
    has_intraday_equities_margin: bool
    id: int
    is_aggregated_at_clearing: bool
    is_closed: bool
    is_closing_only: bool
    is_cryptocurrency_enabled: bool
    is_frozen: bool
    is_full_equity_margin_required: bool
    is_futures_closing_only: bool
    is_futures_intra_day_enabled: bool
    is_futures_enabled: bool
    is_in_day_trade_equity_maintenance_call: bool
    is_in_margin_call: bool
    is_pattern_day_trader: bool
    is_portfolio_margin_enabled: bool
    is_risk_reducing_only: bool
    is_small_notional_futures_intra_day_enabled: bool
    is_roll_the_day_forward_enabled: bool
    are_far_otm_net_options_restricted: bool
    options_level: str
    short_calls_enabled: bool
    small_notional_futures_margin_rate_multiplier: Decimal
    is_equity_offering_enabled: bool
    is_equity_offering_closing_only: bool
    enhanced_fraud_safeguards_enabled_at: datetime
    updated_at: datetime
    day_trade_count: Optional[int] = None
    autotrade_account_type: Optional[str] = None
    clearing_account_number: Optional[str] = None
    clearing_aggregation_identifier: Optional[str] = None
    is_cryptocurrency_closing_only: Optional[bool] = None
    pdt_reset_on: Optional[date] = None
    cmta_override: Optional[int] = None


class Transaction(TastytradeJsonDataclass):
    id: int
    account_number: str
    transaction_type: str
    transaction_sub_type: str
    description: str
    executed_at: datetime
    transaction_date: date
    value: Decimal
    value_effect: str
    net_value: Decimal
    net_value_effect: str
    is_estimated_fee: bool
    symbol: Optional[str] = None
    instrument_type: Optional[str] = None
    underlying_symbol: Optional[str] = None
    action: Optional[str] = None
    quantity: Optional[Decimal] = None
    price: Optional[Decimal] = None
    regulatory_fees: Optional[Decimal] = None
    regulatory_fees_effect: Optional[str] = None
    clearing_fees: Optional[Decimal] = None
    clearing_fees_effect: Optional[str] = None
    commission: Optional[Decimal] = None
    commission_effect: Optional[str] = None
    proprietary_index_option_fees: Optional[Decimal] = None
    proprietary_index_option_fees_effect: Optional[str] = None
    ext_exchange_order_number: Optional[str] = None
    ext_global_order_number: Optional[int] = None
    ext_group_id: Optional[str] = None
    ext_group_fill_id: Optional[str] = None
    ext_exec_id: Optional[str] = None
    exec_id: Optional[str] = None
    exchange: Optional[str] = None
    order_id: Optional[int] = None
    exchange_affiliation_identifier: Optional[str] = None
    leg_count: Optional[int] = None
    destination_venue: Optional[str] = None
    other_charge: Optional[Decimal] = None
    other_charge_effect: Optional[str] = None
    other_charge_description: Optional[str] = None
    reverses_id: Optional[int] = None
    cost_basis_reconciliation_date: Optional[date] = None
    lots: Optional[list[Lot]] = None
    agency_price: Optional[Decimal] = None
    principal_price: Optional[Decimal] = None


class Account(TastytradeJsonDataclass):
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
            accounts.append(cls(**account))

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
        return cls(**account)

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

        data = response.json()['data']

        return TradingStatus(**data)

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

        data = response.json()['data']['items']

        return [AccountBalanceSnapshot(**entry) for entry in data]

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

        data = response.json()['data']['items']

        return [CurrentPosition(**entry) for entry in data]

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

        return [Transaction(**entry) for entry in results]

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

        data = response.json()['data']

        return Transaction(**data)

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

        data = response.json()['data']['items']

        return [NetLiqOhlc(**entry) for entry in data]

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

        data = response.json()['data']

        return PositionLimit(**data)

    def get_effective_margin_requirements(self, session: Session, symbol: str) -> MarginRequirement:
        """
        Get the effective margin requirements for a given symbol.

        :param session: the session to use for the request.
        :param symbol: the symbol to get margin requirements for.

        :return: a :class:`MarginRequirement` object.
        """
        if symbol:
            symbol = symbol.replace('/', '%2F')
        response = requests.get(
            f'{session.base_url}/accounts/{self.account_number}/margin-requirements/{symbol}/effective',
            headers=session.headers
        )
        validate_response(response)

        data = response.json()['data']

        return MarginRequirement(**data)

    def get_margin_requirements(self, session: Session) -> MarginReport:
        """
        Get the margin report for the account, with total margin requirements as well
        as a breakdown per symbol/instrument.

        :param session: the session to use for the request.

        :return: a :class:`MarginReport` object.
        """
        response = requests.get(
            f'{session.base_url}/margin/accounts/{self.account_number}/requirements',
            headers=session.headers
        )
        validate_response(response)

        data = response.json()['data']

        return MarginReport(**data)
