from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal, cast, overload

from pydantic import BaseModel, ConfigDict, model_validator
from typing_extensions import Self

from tastytrade.order import (
    InstrumentType,
    NewComplexOrder,
    NewOrder,
    OrderAction,
    OrderStatus,
    PlacedComplexOrder,
    PlacedComplexOrderResponse,
    PlacedOrder,
    PlacedOrderResponse,
)
from tastytrade.session import Session
from tastytrade.utils import (
    PriceEffect,
    TastytradeData,
    TastytradeError,
    a_paginate,
    paginate,
    set_sign_for,
    today_in_new_york,
)

TT_DATE_FMT = "%Y-%m-%dT%H:%M:%SZ"


class EmptyDict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AccountBalance(TastytradeData):
    """
    Dataclass containing account balance information.
    """

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
    long_cryptocurrency_value: Decimal
    short_cryptocurrency_value: Decimal
    cryptocurrency_margin_requirement: Decimal
    unsettled_cryptocurrency_fiat_amount: Decimal
    closed_loop_available_balance: Decimal
    equity_offering_margin_requirement: Decimal
    long_bond_value: Decimal
    bond_margin_requirement: Decimal
    used_derivative_buying_power: Decimal
    snapshot_date: date
    reg_t_margin_requirement: Decimal
    futures_overnight_margin_requirement: Decimal
    futures_intraday_margin_requirement: Decimal
    maintenance_excess: Decimal
    pending_margin_interest: Decimal
    effective_cryptocurrency_buying_power: Decimal
    updated_at: datetime
    apex_starting_day_margin_equity: Decimal | None = None
    buying_power_adjustment: Decimal | None = None
    time_of_day: str | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_price_effects(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data = cast(dict[str, Any], data)
            key = "unsettled-cryptocurrency-fiat-amount"
            if (
                data.get("unsettled-cryptocurrency-fiat-effect")
                == PriceEffect.DEBIT.value
            ):
                data[key] = -abs(Decimal(data[key]))
        return set_sign_for(data, ["pending_cash", "buying_power_adjustment"])


class AccountBalanceSnapshot(TastytradeData):
    """
    Dataclass containing account balance for a moment in time (snapshot).
    """

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
    snapshot_date: date
    time_of_day: str | None = None
    long_cryptocurrency_value: Decimal | None = None
    short_cryptocurrency_value: Decimal | None = None
    cryptocurrency_margin_requirement: Decimal | None = None
    unsettled_cryptocurrency_fiat_amount: Decimal | None = None
    closed_loop_available_balance: Decimal | None = None
    equity_offering_margin_requirement: Decimal | None = None
    long_bond_value: Decimal | None = None
    bond_margin_requirement: Decimal | None = None
    used_derivative_buying_power: Decimal | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_price_effects(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data = cast(dict[str, Any], data)
            key = "unsettled-cryptocurrency-fiat-amount"
            if data.get("unsettled-cryptocurrency-fiat-effect") == PriceEffect.DEBIT:
                data[key] = -abs(Decimal(data[key]))
        return set_sign_for(data, ["pending_cash"])


class CurrentPosition(TastytradeData):
    """
    Dataclass containing imformation about an individual position in a
    portfolio.
    """

    account_number: str
    symbol: str
    instrument_type: InstrumentType
    underlying_symbol: str
    quantity: Decimal
    quantity_direction: str
    close_price: Decimal
    average_open_price: Decimal
    multiplier: int
    cost_effect: str
    is_suppressed: bool
    is_frozen: bool
    realized_day_gain: Decimal
    realized_today: Decimal
    created_at: datetime
    updated_at: datetime
    mark: Decimal | None = None
    mark_price: Decimal | None = None
    restricted_quantity: Decimal | None = None
    expires_at: datetime | None = None
    fixing_price: Decimal | None = None
    deliverable_type: str | None = None
    average_yearly_market_close_price: Decimal | None = None
    average_daily_market_close_price: Decimal | None = None
    realized_day_gain_date: date | None = None
    realized_today_date: date | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_price_effects(cls, data: Any) -> Any:
        return set_sign_for(data, ["realized_day_gain", "realized_today"])


class FeesInfo(TastytradeData):
    total_fees: Decimal

    @model_validator(mode="before")
    @classmethod
    def validate_price_effects(cls, data: Any) -> Any:
        return set_sign_for(data, ["total_fees"])


class Lot(TastytradeData):
    """
    Dataclass containing information about the lot of a position.
    """

    id: str
    transaction_id: int
    quantity: Decimal
    price: Decimal
    quantity_direction: str
    executed_at: datetime
    transaction_date: date


class MarginReportEntry(TastytradeData):
    """
    Dataclass containing an individual entry (relating to a specific position)
    as part of the overall margin report.
    """

    description: str
    code: str
    buying_power: Decimal
    margin_calculation_type: str
    margin_requirement: Decimal
    expected_price_range_up_percent: Decimal | None = None
    expected_price_range_down_percent: Decimal | None = None
    groups: list[dict[str, Any]] | None = None
    initial_requirement: Decimal | None = None
    maintenance_requirement: Decimal | None = None
    point_of_no_return_percent: Decimal | None = None
    price_increase_percent: Decimal | None = None
    price_decrease_percent: Decimal | None = None
    underlying_symbol: str | None = None
    underlying_type: str | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_price_effects(cls, data: Any) -> Any:
        return set_sign_for(
            data,
            [
                "buying_power",
                "margin_requirement",
                "initial_requirement",
                "maintenance_requirement",
            ],
        )


class MarginReport(TastytradeData):
    """
    Dataclass containing an overall portfolio margin report.
    """

    account_number: str
    description: str
    margin_calculation_type: str
    option_level: str
    margin_requirement: Decimal
    maintenance_requirement: Decimal
    margin_equity: Decimal
    option_buying_power: Decimal
    reg_t_margin_requirement: Decimal
    reg_t_option_buying_power: Decimal
    maintenance_excess: Decimal
    last_state_timestamp: int
    groups: list[MarginReportEntry | EmptyDict]
    initial_requirement: Decimal | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_price_effects(cls, data: Any) -> Any:
        return set_sign_for(
            data,
            [
                "maintenance_requirement",
                "margin_requirement",
                "margin_equity",
                "maintenance_excess",
                "option_buying_power",
                "reg_t_margin_requirement",
                "reg_t_option_buying_power",
                "initial_requirement",
            ],
        )


class NetLiqOhlc(TastytradeData):
    """
    Dataclass containing historical net liquidation data in OHLC format
    (open, high, low, close), with a timestamp.
    """

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
    time: str


class TradingStatus(TastytradeData):
    """
    Dataclass containing information about an account's trading status, such
    as what types of trades are allowed (e.g. margin, crypto, futures)
    """

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
    is_small_notional_futures_intra_day_enabled: bool
    is_roll_the_day_forward_enabled: bool
    are_far_otm_net_options_restricted: bool
    options_level: str
    short_calls_enabled: bool
    small_notional_futures_margin_rate_multiplier: Decimal
    is_equity_offering_enabled: bool
    is_equity_offering_closing_only: bool
    updated_at: datetime
    is_portfolio_margin_enabled: bool | None = None
    is_risk_reducing_only: bool | None = None
    day_trade_count: int | None = None
    autotrade_account_type: str | None = None
    clearing_account_number: str | None = None
    clearing_aggregation_identifier: str | None = None
    is_cryptocurrency_closing_only: bool | None = None
    pdt_reset_on: date | None = None
    cmta_override: int | None = None
    enhanced_fraud_safeguards_enabled_at: datetime | None = None


class Transaction(TastytradeData):
    """
    Dataclass containing information about a past transaction.
    """

    id: int
    account_number: str
    transaction_type: str
    transaction_sub_type: str
    description: str
    executed_at: datetime
    transaction_date: date
    value: Decimal
    net_value: Decimal
    is_estimated_fee: bool
    symbol: str | None = None
    instrument_type: InstrumentType | None = None
    underlying_symbol: str | None = None
    action: OrderAction | None = None
    quantity: Decimal | None = None
    price: Decimal | None = None
    regulatory_fees: Decimal | None = None
    clearing_fees: Decimal | None = None
    commission: Decimal | None = None
    proprietary_index_option_fees: Decimal | None = None
    ext_exchange_order_number: str | None = None
    ext_global_order_number: int | None = None
    ext_group_id: str | None = None
    ext_group_fill_id: str | None = None
    ext_exec_id: str | None = None
    exec_id: str | None = None
    exchange: str | None = None
    order_id: int | None = None
    exchange_affiliation_identifier: str | None = None
    leg_count: int | None = None
    destination_venue: str | None = None
    other_charge: Decimal | None = None
    other_charge_description: str | None = None
    reverses_id: int | None = None
    cost_basis_reconciliation_date: date | None = None
    lots: list[Lot] | None = None
    agency_price: Decimal | None = None
    principal_price: Decimal | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_price_effects(cls, data: Any) -> Any:
        return set_sign_for(
            data,
            [
                "value",
                "net_value",
                "regulatory_fees",
                "clearing_fees",
                "proprietary_index_option_fees",
                "commission",
                "other_charge",
            ],
        )


class Account(TastytradeData):
    """
    Dataclass that represents a Tastytrade account object, containing
    methods for retrieving information about the account, placing orders,
    and retrieving past transactions.
    """

    account_number: str
    opened_at: datetime
    nickname: str
    account_type_name: str
    is_closed: bool
    day_trader_status: str | bool
    is_firm_error: bool
    is_firm_proprietary: bool
    is_futures_approved: bool
    is_test_drive: bool = False
    margin_or_cash: str
    is_foreign: bool
    created_at: datetime
    external_id: str | None = None
    closed_at: str | None = None
    funding_date: date | None = None
    investment_objective: str | None = None
    liquidity_needs: str | None = None
    risk_tolerance: str | None = None
    investment_time_horizon: str | None = None
    futures_account_purpose: str | None = None
    external_fdid: str | None = None
    suitable_options_level: str | None = None
    submitting_user_id: str | None = None

    @overload
    @classmethod
    async def a_get(
        cls, session: Session, *, include_closed: bool = False
    ) -> list[Self]: ...

    @overload
    @classmethod
    async def a_get(cls, session: Session, account_number: str) -> Self: ...

    @classmethod
    async def a_get(
        cls,
        session: Session,
        account_number: str | None = None,
        include_closed: bool = False,
    ) -> Self | list[Self]:
        """
        Gets all trading accounts associated with the Tastytrade user, or a specific
        one if given an account ID.

        :param session: the session to use for the request.
        :param account_number: the account ID to get.
        :param include_closed: whether to include closed accounts in the results
        """
        if account_number:
            data = await session._a_get(f"/customers/me/accounts/{account_number}")
            return cls(**data)
        data = await session._a_get("/customers/me/accounts")
        return [
            cls(**i["account"])
            for i in data["items"]
            if include_closed or not i["account"]["is-closed"]
        ]

    @overload
    @classmethod
    def get(cls, session: Session, *, include_closed: bool = False) -> list[Self]: ...

    @overload
    @classmethod
    def get(cls, session: Session, account_number: str) -> Self: ...

    @classmethod
    def get(
        cls,
        session: Session,
        account_number: str | None = None,
        include_closed: bool = False,
    ) -> Self | list[Self]:
        """
        Gets all trading accounts associated with the Tastytrade user, or a specific
        one if given an account ID.

        :param session: the session to use for the request.
        :param account_number: the account ID to get.
        :param include_closed: whether to include closed accounts in the results
        """
        if account_number:
            data = session._get(f"/customers/me/accounts/{account_number}")
            return cls(**data)
        data = session._get("/customers/me/accounts")
        return [
            cls(**i["account"])
            for i in data["items"]
            if include_closed or not i["account"]["is-closed"]
        ]

    async def a_get_trading_status(self, session: Session) -> TradingStatus:
        """
        Get the trading status of the account.

        :param session: the session to use for the request.
        """
        data = await session._a_get(f"/accounts/{self.account_number}/trading-status")
        return TradingStatus(**data)

    def get_trading_status(self, session: Session) -> TradingStatus:
        """
        Get the trading status of the account.

        :param session: the session to use for the request.
        """
        data = session._get(f"/accounts/{self.account_number}/trading-status")
        return TradingStatus(**data)

    async def a_get_balances(
        self, session: Session, currency: str = "USD"
    ) -> AccountBalance:
        """
        Get the current balances of the account.

        :param session: the session to use for the request
        :param currency: the currency to state balances in
        """
        data = await session._a_get(
            f"/accounts/{self.account_number}/balances/{currency}"
        )
        return AccountBalance(**data)

    def get_balances(self, session: Session, currency: str = "USD") -> AccountBalance:
        """
        Get the current balances of the account.

        :param session: the session to use for the request
        :param currency: the currency to state balances in
        """
        data = session._get(f"/accounts/{self.account_number}/balances/{currency}")
        return AccountBalance(**data)

    async def a_get_balance_snapshots(
        self,
        session: Session,
        per_page: int = 250,
        page_offset: int | None = 0,
        currency: str = "USD",
        end_date: date | None = None,
        start_date: date | None = None,
        snapshot_date: date | None = None,
        time_of_day: Literal["BOD", "EOD"] = "EOD",
    ) -> list[AccountBalanceSnapshot]:
        """
        Returns a list of balance snapshots. This list will
        just have a few snapshots if you don't pass a start
        date; otherwise, it will be each day's balances in
        the given range.

        :param session: the session to use for the request.
        :param per_page: the number of results to return per page.
        :param page_offset:
            provide a specific page to get; if None, get all pages
        :param currency: the currency to show balances in.
        :param start_date: the starting date of the range.
        :param end_date: the ending date of the range.
        :param snapshot_date: the date of the snapshot to get.
        :param time_of_day:
            the time of day of the snapshots to get, either 'EOD' (End Of Day) or 'BOD'
            (Beginning Of Day).
        """
        params = {
            "per-page": per_page,
            "page-offset": page_offset,
            "currency": currency,
            "end-date": end_date,
            "start-date": start_date,
            "snapshot-date": snapshot_date,
            "time-of-day": time_of_day,
        }
        return await a_paginate(
            session.async_client,
            AccountBalanceSnapshot,
            f"/accounts/{self.account_number}/balance-snapshots",
            params,
        )

    def get_balance_snapshots(
        self,
        session: Session,
        per_page: int = 250,
        page_offset: int | None = 0,
        currency: str = "USD",
        end_date: date | None = None,
        start_date: date | None = None,
        snapshot_date: date | None = None,
        time_of_day: Literal["BOD", "EOD"] = "EOD",
    ) -> list[AccountBalanceSnapshot]:
        """
        Returns a list of balance snapshots. This list will
        just have a few snapshots if you don't pass a start
        date; otherwise, it will be each day's balances in
        the given range.

        :param session: the session to use for the request.
        :param per_page: the number of results to return per page.
        :param page_offset:
            provide a specific page to get; if None, get all pages
        :param currency: the currency to show balances in.
        :param start_date: the starting date of the range.
        :param end_date: the ending date of the range.
        :param snapshot_date: the date of the snapshot to get.
        :param time_of_day:
            the time of day of the snapshots to get, either 'EOD' (End Of Day) or 'BOD'
            (Beginning Of Day).
        """
        params = {
            "per-page": per_page,
            "page-offset": page_offset,
            "currency": currency,
            "end-date": end_date,
            "start-date": start_date,
            "snapshot-date": snapshot_date,
            "time-of-day": time_of_day,
        }
        return paginate(
            session.sync_client,
            AccountBalanceSnapshot,
            f"/accounts/{self.account_number}/balance-snapshots",
            params,
        )

    async def a_get_positions(
        self,
        session: Session,
        underlying_symbols: list[str] | None = None,
        symbol: str | None = None,
        instrument_type: InstrumentType | None = None,
        include_closed: bool | None = None,
        underlying_product_code: str | None = None,
        partition_keys: list[str] | None = None,
        net_positions: bool | None = None,
        include_marks: bool | None = None,
    ) -> list[CurrentPosition]:
        """
        Get the current positions of the account.

        :param session: the session to use for the request.
        :param underlying_symbols:
            an array of underlying symbols for positions.
        :param symbol: a single symbol.
        :param instrument_type: the type of instrument.
        :param include_closed:
            if closed positions should be included in the query.
        :param underlying_product_code: the underlying future's product code.
        :param partition_keys: account partition keys.
        :param net_positions:
            returns net positions grouped by instrument type and symbol.
        :param include_marks:
            include current quote mark (note: can decrease performance).
        """
        params = {
            "underlying-symbol[]": underlying_symbols,
            "symbol": symbol,
            "instrument-type": instrument_type.value if instrument_type else None,
            "include-closed-positions": include_closed,
            "underlying-product-code": underlying_product_code,
            "partition-keys[]": partition_keys,
            "net-positions": net_positions,
            "include-marks": include_marks,
        }
        data = await session._a_get(
            f"/accounts/{self.account_number}/positions",
            params={k: v for k, v in params.items() if v is not None},
        )
        return [CurrentPosition(**i) for i in data["items"]]

    def get_positions(
        self,
        session: Session,
        underlying_symbols: list[str] | None = None,
        symbol: str | None = None,
        instrument_type: InstrumentType | None = None,
        include_closed: bool | None = None,
        underlying_product_code: str | None = None,
        partition_keys: list[str] | None = None,
        net_positions: bool | None = None,
        include_marks: bool | None = None,
    ) -> list[CurrentPosition]:
        """
        Get the current positions of the account.

        :param session: the session to use for the request.
        :param underlying_symbols:
            an array of underlying symbols for positions.
        :param symbol: a single symbol.
        :param instrument_type: the type of instrument.
        :param include_closed:
            if closed positions should be included in the query.
        :param underlying_product_code: the underlying future's product code.
        :param partition_keys: account partition keys.
        :param net_positions:
            returns net positions grouped by instrument type and symbol.
        :param include_marks:
            include current quote mark (note: can decrease performance).
        """
        params = {
            "underlying-symbol[]": underlying_symbols,
            "symbol": symbol,
            "instrument-type": instrument_type.value if instrument_type else None,
            "include-closed-positions": include_closed,
            "underlying-product-code": underlying_product_code,
            "partition-keys[]": partition_keys,
            "net-positions": net_positions,
            "include-marks": include_marks,
        }
        data = session._get(
            f"/accounts/{self.account_number}/positions",
            params={k: v for k, v in params.items() if v is not None},
        )
        return [CurrentPosition(**i) for i in data["items"]]

    async def a_get_history(
        self,
        session: Session,
        per_page: int = 250,
        page_offset: int | None = 0,
        sort: Literal["Asc", "Desc"] = "Desc",
        type: str | None = None,
        types: list[str] | None = None,
        sub_types: list[str] | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        instrument_type: InstrumentType | None = None,
        symbol: str | None = None,
        underlying_symbol: str | None = None,
        action: str | None = None,
        partition_key: str | None = None,
        futures_symbol: str | None = None,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
    ) -> list[Transaction]:
        """
        Get transaction history of the account.

        :param session: the session to use for the request.
        :param per_page: the number of results to return per page.
        :param page_offset:
            provide a specific page to get; if None, get all pages
        :param sort: the order to sort results in, either 'Desc' or 'Asc'.
        :param type: the type of transaction.
        :param types: a list of transaction types to filter by.
        :param sub_types: an array of transaction subtypes to filter by.
        :param start_date: the start date of transactions to query.
        :param end_date: the end date of transactions to query.
        :param instrument_type: the type of instrument.
        :param symbol: a single symbol.
        :param underlying_symbol: the underlying symbol.
        :param action:
            the action of the transaction: 'Sell to Open', 'Sell to Close',
            'Buy to Open', 'Buy to Close', 'Sell' or 'Buy'.
        :param partition_key: account partition key.
        :param futures_symbol: the full TW Future Symbol, e.g. /ESZ9, /NGZ19.
        :param start_at:
            datetime start range for filtering transactions in full date-time.
        :param end_at:
            datetime end range for filtering transactions in full date-time.
        """
        params = {
            "per-page": per_page,
            "page-offset": page_offset,
            "sort": sort,
            "type": type,
            "types[]": types,
            "sub-type[]": sub_types,
            "start-date": start_date,
            "end-date": end_date,
            "instrument-type": instrument_type.value if instrument_type else None,
            "symbol": symbol,
            "underlying-symbol": underlying_symbol,
            "action": action,
            "partition-key": partition_key,
            "futures-symbol": futures_symbol,
            "start-at": start_at,
            "end-at": end_at,
        }
        return await a_paginate(
            session.async_client,
            Transaction,
            f"/accounts/{self.account_number}/transactions",
            params,
        )

    def get_history(
        self,
        session: Session,
        per_page: int = 250,
        page_offset: int | None = 0,
        sort: Literal["Asc", "Desc"] = "Desc",
        type: str | None = None,
        types: list[str] | None = None,
        sub_types: list[str] | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        instrument_type: InstrumentType | None = None,
        symbol: str | None = None,
        underlying_symbol: str | None = None,
        action: str | None = None,
        partition_key: str | None = None,
        futures_symbol: str | None = None,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
    ) -> list[Transaction]:
        """
        Get transaction history of the account.

        :param session: the session to use for the request.
        :param per_page: the number of results to return per page.
        :param page_offset:
            provide a specific page to get; if None, get all pages
        :param sort: the order to sort results in, either 'Desc' or 'Asc'.
        :param type: the type of transaction.
        :param types: a list of transaction types to filter by.
        :param sub_types: an array of transaction subtypes to filter by.
        :param start_date: the start date of transactions to query.
        :param end_date: the end date of transactions to query.
        :param instrument_type: the type of instrument.
        :param symbol: a single symbol.
        :param underlying_symbol: the underlying symbol.
        :param action:
            the action of the transaction: 'Sell to Open', 'Sell to Close',
            'Buy to Open', 'Buy to Close', 'Sell' or 'Buy'.
        :param partition_key: account partition key.
        :param futures_symbol: the full TW Future Symbol, e.g. /ESZ9, /NGZ19.
        :param start_at:
            datetime start range for filtering transactions in full date-time.
        :param end_at:
            datetime end range for filtering transactions in full date-time.
        """
        params = {
            "per-page": per_page,
            "page-offset": page_offset,
            "sort": sort,
            "type": type,
            "types[]": types,
            "sub-type[]": sub_types,
            "start-date": start_date,
            "end-date": end_date,
            "instrument-type": instrument_type.value if instrument_type else None,
            "symbol": symbol,
            "underlying-symbol": underlying_symbol,
            "action": action,
            "partition-key": partition_key,
            "futures-symbol": futures_symbol,
            "start-at": start_at,
            "end-at": end_at,
        }
        return paginate(
            session.sync_client,
            Transaction,
            f"/accounts/{self.account_number}/transactions",
            params,
        )

    async def a_get_transaction(self, session: Session, id: int) -> Transaction:
        """
        Get a single transaction by ID.

        :param session: the session to use for the request.
        :param id: the ID of the transaction to fetch.
        """
        data = await session._a_get(
            f"/accounts/{self.account_number}/transactions/{id}"
        )
        return Transaction(**data)

    def get_transaction(self, session: Session, id: int) -> Transaction:
        """
        Get a single transaction by ID.

        :param session: the session to use for the request.
        :param id: the ID of the transaction to fetch.
        """
        data = session._get(f"/accounts/{self.account_number}/transactions/{id}")
        return Transaction(**data)

    async def a_get_total_fees(
        self, session: Session, day: date | None = None
    ) -> FeesInfo:
        """
        Get the total fees for a given date.

        :param session: the session to use for the request.
        :param day: the date to get fees for.
        """
        if not day:
            day = today_in_new_york()
        data = await session._a_get(
            f"/accounts/{self.account_number}/transactions/total-fees",
            params={"date": day},
        )
        return FeesInfo(**data)

    def get_total_fees(self, session: Session, day: date | None = None) -> FeesInfo:
        """
        Get the total fees for a given date.

        :param session: the session to use for the request.
        :param day: the date to get fees for.
        """
        if not day:
            day = today_in_new_york()
        data = session._get(
            f"/accounts/{self.account_number}/transactions/total-fees",
            params={"date": day},
        )
        return FeesInfo(**data)

    async def a_get_net_liquidating_value_history(
        self,
        session: Session,
        time_back: str | None = None,
        start_time: datetime | None = None,
    ) -> list[NetLiqOhlc]:
        """
        Returns a list of account net liquidating value snapshots over the
        specified time period.

        :param session:
            the session to use for the request, can't be certification.
        :param time_back:
            the time period to get net liquidating value snapshots for. This
            param is required if start_time is not given. Possible values are:
            '1d', '1m', '3m', '6m', '1y', 'all'.
        :param start_time:
            the start point for the query. This param is required is time-back
            is not given. If given, will take precedence over time-back.
        """
        params = {}
        if start_time:
            # format to Tastytrade DateTime format
            params = {"start-time": start_time.strftime(TT_DATE_FMT)}
        elif not time_back:
            msg = "Either time_back or start_time must be specified."
            raise TastytradeError(msg)
        else:
            params = {"time-back": time_back}
        data = await session._a_get(
            f"/accounts/{self.account_number}/net-liq/history", params=params
        )
        return [NetLiqOhlc(**i) for i in data["items"]]

    def get_net_liquidating_value_history(
        self,
        session: Session,
        time_back: str | None = None,
        start_time: datetime | None = None,
    ) -> list[NetLiqOhlc]:
        """
        Returns a list of account net liquidating value snapshots over the
        specified time period.

        :param session:
            the session to use for the request, can't be certification.
        :param time_back:
            the time period to get net liquidating value snapshots for. This
            param is required if start_time is not given. Possible values are:
            '1d', '1m', '3m', '6m', '1y', 'all'.
        :param start_time:
            the start point for the query. This param is required is time-back
            is not given. If given, will take precedence over time-back.
        """
        params = {}
        if start_time:
            # format to Tastytrade DateTime format
            params = {"start-time": start_time.strftime(TT_DATE_FMT)}
        elif not time_back:
            msg = "Either time_back or start_time must be specified."
            raise TastytradeError(msg)
        else:
            params = {"time-back": time_back}
        data = session._get(
            f"/accounts/{self.account_number}/net-liq/history", params=params
        )
        return [NetLiqOhlc(**i) for i in data["items"]]

    async def a_get_margin_requirements(self, session: Session) -> MarginReport:
        """
        Get the margin report for the account, with total margin requirements
        as well as a breakdown per symbol/instrument.

        :param session: the session to use for the request.
        """
        data = await session._a_get(
            f"/margin/accounts/{self.account_number}/requirements"
        )
        return MarginReport(**data)

    def get_margin_requirements(self, session: Session) -> MarginReport:
        """
        Get the margin report for the account, with total margin requirements
        as well as a breakdown per symbol/instrument.

        :param session: the session to use for the request.
        """
        data = session._get(f"/margin/accounts/{self.account_number}/requirements")
        return MarginReport(**data)

    async def a_get_live_orders(self, session: Session) -> list[PlacedOrder]:
        """
        Get orders placed today for the account.

        :param session: the session to use for the request.
        """
        data = await session._a_get(f"/accounts/{self.account_number}/orders/live")
        return [PlacedOrder(**i) for i in data["items"]]

    def get_live_orders(self, session: Session) -> list[PlacedOrder]:
        """
        Get orders placed today for the account.

        :param session: the session to use for the request.
        """
        data = session._get(f"/accounts/{self.account_number}/orders/live")
        return [PlacedOrder(**i) for i in data["items"]]

    async def a_get_live_complex_orders(
        self, session: Session
    ) -> list[PlacedComplexOrder]:
        """
        Get complex orders placed today for the account.

        :param session: the session to use for the request.
        """
        data = await session._a_get(
            f"/accounts/{self.account_number}/complex-orders/live"
        )
        return [PlacedComplexOrder(**i) for i in data["items"]]

    def get_live_complex_orders(self, session: Session) -> list[PlacedComplexOrder]:
        """
        Get complex orders placed today for the account.

        :param session: the session to use for the request.
        """
        data = session._get(f"/accounts/{self.account_number}/complex-orders/live")
        return [PlacedComplexOrder(**i) for i in data["items"]]

    async def a_get_complex_order(
        self, session: Session, order_id: int
    ) -> PlacedComplexOrder:
        """
        Gets a complex order with the given ID.

        :param session: the session to use for the request.
        :param order_id: the ID of the order to fetch.
        """
        data = await session._a_get(
            f"/accounts/{self.account_number}/complex-orders/{order_id}"
        )
        return PlacedComplexOrder(**data)

    def get_complex_order(self, session: Session, order_id: int) -> PlacedComplexOrder:
        """
        Gets a complex order with the given ID.

        :param session: the session to use for the request.
        :param order_id: the ID of the order to fetch.
        """
        data = session._get(
            f"/accounts/{self.account_number}/complex-orders/{order_id}"
        )
        return PlacedComplexOrder(**data)

    async def a_get_order(self, session: Session, order_id: int) -> PlacedOrder:
        """
        Gets an order with the given ID.

        :param session: the session to use for the request.
        :param order_id: the ID of the order to fetch.
        """
        data = await session._a_get(
            f"/accounts/{self.account_number}/orders/{order_id}"
        )
        return PlacedOrder(**data)

    def get_order(self, session: Session, order_id: int) -> PlacedOrder:
        """
        Gets an order with the given ID.

        :param session: the session to use for the request.
        :param order_id: the ID of the order to fetch.
        """
        data = session._get(f"/accounts/{self.account_number}/orders/{order_id}")
        return PlacedOrder(**data)

    async def a_delete_complex_order(self, session: Session, order_id: int) -> None:
        """
        Delete a complex order by ID.

        :param session: the session to use for the request.
        :param order_id: the ID of the order to delete.
        """
        await session._a_delete(
            f"/accounts/{self.account_number}/complex-orders/{order_id}"
        )

    def delete_complex_order(self, session: Session, order_id: int) -> None:
        """
        Delete a complex order by ID.

        :param session: the session to use for the request.
        :param order_id: the ID of the order to delete.
        """
        session._delete(f"/accounts/{self.account_number}/complex-orders/{order_id}")

    async def a_delete_order(self, session: Session, order_id: int) -> None:
        """
        Delete an order by ID.

        :param session: the session to use for the request.
        :param order_id: the ID of the order to delete.
        """
        await session._a_delete(f"/accounts/{self.account_number}/orders/{order_id}")

    def delete_order(self, session: Session, order_id: int) -> None:
        """
        Delete an order by ID.

        :param session: the session to use for the request.
        :param order_id: the ID of the order to delete.
        """
        session._delete(f"/accounts/{self.account_number}/orders/{order_id}")

    async def a_get_order_history(
        self,
        session: Session,
        per_page: int = 50,
        page_offset: int | None = 0,
        start_date: date | None = None,
        end_date: date | None = None,
        underlying_symbol: str | None = None,
        statuses: list[OrderStatus] | None = None,
        futures_symbol: str | None = None,
        underlying_instrument_type: InstrumentType | None = None,
        sort: Literal["Asc", "Desc"] | None = None,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
    ) -> list[PlacedOrder]:
        """
        Get order history of the account.

        :param session: the session to use for the request.
        :param per_page: the number of results to return per page.
        :param page_offset:
            provide a specific page to get; if None, get all pages
        :param start_date: the start date of orders to query.
        :param end_date: the end date of orders to query.
        :param underlying_symbol: underlying symbol to filter by.
        :param statuses: a list of statuses to filter by.
        :param futures_symbol:
            Tastytrade future symbol for futures and future options.
        :param underlying_instrument_type: the type of instrument to filter by
        :param sort: the order to sort results in, either 'Desc' or 'Asc'.
        :param start_at:
            datetime start range for filtering transactions in full date-time.
        :param end_at:
            datetime end range for filtering transactions in full date-time.
        """
        params = {
            "per-page": per_page,
            "page-offset": page_offset,
            "start-date": start_date,
            "end-date": end_date,
            "underlying-symbol": underlying_symbol,
            "status[]": [s.value for s in statuses] if statuses else None,
            "futures-symbol": futures_symbol,
            "underlying-instrument-type": underlying_instrument_type.value
            if underlying_instrument_type
            else None,
            "sort": sort,
            "start-at": start_at,
            "end-at": end_at,
        }
        return await a_paginate(
            session.async_client,
            PlacedOrder,
            f"/accounts/{self.account_number}/orders",
            params,
        )

    def get_order_history(
        self,
        session: Session,
        per_page: int = 50,
        page_offset: int | None = 0,
        start_date: date | None = None,
        end_date: date | None = None,
        underlying_symbol: str | None = None,
        statuses: list[OrderStatus] | None = None,
        futures_symbol: str | None = None,
        underlying_instrument_type: InstrumentType | None = None,
        sort: Literal["Asc", "Desc"] | None = None,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
    ) -> list[PlacedOrder]:
        """
        Get order history of the account.

        :param session: the session to use for the request.
        :param per_page: the number of results to return per page.
        :param page_offset:
            provide a specific page to get; if None, get all pages
        :param start_date: the start date of orders to query.
        :param end_date: the end date of orders to query.
        :param underlying_symbol: underlying symbol to filter by.
        :param statuses: a list of statuses to filter by.
        :param futures_symbol:
            Tastytrade future symbol for futures and future options.
        :param underlying_instrument_type: the type of instrument to filter by
        :param sort: the order to sort results in, either 'Desc' or 'Asc'.
        :param start_at:
            datetime start range for filtering transactions in full date-time.
        :param end_at:
            datetime end range for filtering transactions in full date-time.
        """
        params = {
            "per-page": per_page,
            "page-offset": page_offset,
            "start-date": start_date,
            "end-date": end_date,
            "underlying-symbol": underlying_symbol,
            "status[]": [s.value for s in statuses] if statuses else None,
            "futures-symbol": futures_symbol,
            "underlying-instrument-type": underlying_instrument_type.value
            if underlying_instrument_type
            else None,
            "sort": sort,
            "start-at": start_at,
            "end-at": end_at,
        }
        return paginate(
            session.sync_client,
            PlacedOrder,
            f"/accounts/{self.account_number}/orders",
            params,
        )

    async def a_get_complex_order_history(
        self, session: Session, per_page: int = 50, page_offset: int | None = 0
    ) -> list[PlacedComplexOrder]:
        """
        Get order history of the account.

        :param session: the session to use for the request.
        :param per_page: the number of results to return per page.
        :param page_offset:
            provide a specific page to get; if None, get all pages
        """
        params = {"per-page": per_page, "page-offset": page_offset}
        return await a_paginate(
            session.async_client,
            PlacedComplexOrder,
            f"/accounts/{self.account_number}/complex-orders",
            params,
        )

    def get_complex_order_history(
        self, session: Session, per_page: int = 50, page_offset: int | None = 0
    ) -> list[PlacedComplexOrder]:
        """
        Get order history of the account.

        :param session: the session to use for the request.
        :param per_page: the number of results to return per page.
        :param page_offset:
            provide a specific page to get; if None, get all pages
        """
        params = {"per-page": per_page, "page-offset": page_offset}
        return paginate(
            session.sync_client,
            PlacedComplexOrder,
            f"/accounts/{self.account_number}/complex-orders",
            params,
        )

    async def a_place_order(
        self, session: Session, order: NewOrder, dry_run: bool = True
    ) -> PlacedOrderResponse:
        """
        Place the given order.

        :param session: the session to use for the request.
        :param order: the order to place.
        :param dry_run: whether this is a test order or not.
        """
        url = f"/accounts/{self.account_number}/orders"
        if dry_run:
            url += "/dry-run"
        json = order.model_dump_json(exclude_none=True, by_alias=True)
        data = await session._a_post(url, data=json)
        return PlacedOrderResponse(**data)

    def place_order(
        self, session: Session, order: NewOrder, dry_run: bool = True
    ) -> PlacedOrderResponse:
        """
        Place the given order.

        :param session: the session to use for the request.
        :param order: the order to place.
        :param dry_run: whether this is a test order or not.
        """
        url = f"/accounts/{self.account_number}/orders"
        if dry_run:
            url += "/dry-run"
        json = order.model_dump_json(exclude_none=True, by_alias=True)
        data = session._post(url, data=json)
        return PlacedOrderResponse(**data)

    async def a_place_complex_order(
        self, session: Session, order: NewComplexOrder, dry_run: bool = True
    ) -> PlacedComplexOrderResponse:
        """
        Place the given order.

        :param session: the session to use for the request.
        :param order: the order to place.
        :param dry_run: whether this is a test order or not.
        """
        url = f"/accounts/{self.account_number}/complex-orders"
        if dry_run:
            url += "/dry-run"
        json = order.model_dump_json(exclude_none=True, by_alias=True)
        data = await session._a_post(url, data=json)
        return PlacedComplexOrderResponse(**data)

    def place_complex_order(
        self, session: Session, order: NewComplexOrder, dry_run: bool = True
    ) -> PlacedComplexOrderResponse:
        """
        Place the given order.

        :param session: the session to use for the request.
        :param order: the order to place.
        :param dry_run: whether this is a test order or not.
        """
        url = f"/accounts/{self.account_number}/complex-orders"
        if dry_run:
            url += "/dry-run"
        json = order.model_dump_json(exclude_none=True, by_alias=True)
        data = session._post(url, data=json)
        return PlacedComplexOrderResponse(**data)

    async def a_replace_order(
        self, session: Session, old_order_id: int, new_order: NewOrder
    ) -> PlacedOrder:
        """
        Replace an order with a new order with different characteristics (but
        same legs).

        :param session: the session to use for the request.
        :param old_order_id: the ID of the order to replace.
        :param new_order: the new order to replace the old order with.
        """
        data = await session._a_put(
            f"/accounts/{self.account_number}/orders/{old_order_id}",
            data=new_order.model_dump_json(
                exclude={"legs"}, exclude_none=True, by_alias=True
            ),
        )
        return PlacedOrder(**data)

    def replace_order(
        self, session: Session, old_order_id: int, new_order: NewOrder
    ) -> PlacedOrder:
        """
        Replace an order with a new order with different characteristics (but
        same legs).

        :param session: the session to use for the request.
        :param old_order_id: the ID of the order to replace.
        :param new_order: the new order to replace the old order with.
        """
        data = session._put(
            f"/accounts/{self.account_number}/orders/{old_order_id}",
            data=new_order.model_dump_json(
                exclude={"legs"}, exclude_none=True, by_alias=True
            ),
        )
        return PlacedOrder(**data)
