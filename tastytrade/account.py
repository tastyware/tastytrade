from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal, Optional, Union

import httpx
from pydantic import BaseModel, model_validator
from typing_extensions import Self

from tastytrade import VAST_URL
from tastytrade.order import (
    InstrumentType,
    NewComplexOrder,
    NewOrder,
    OrderAction,
    OrderChain,
    OrderStatus,
    PlacedComplexOrder,
    PlacedComplexOrderResponse,
    PlacedOrder,
    PlacedOrderResponse,
)
from tastytrade.session import Session
from tastytrade.utils import (
    PriceEffect,
    TastytradeError,
    TastytradeJsonDataclass,
    _set_sign_for,
    today_in_new_york,
    validate_response,
)

TT_DATE_FMT = "%Y-%m-%dT%H:%M:%SZ"


class EmptyDict(BaseModel):
    class Config:
        extra = "forbid"


class AccountBalance(TastytradeJsonDataclass):
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
    snapshot_date: date
    reg_t_margin_requirement: Decimal
    futures_overnight_margin_requirement: Decimal
    futures_intraday_margin_requirement: Decimal
    maintenance_excess: Decimal
    pending_margin_interest: Decimal
    effective_cryptocurrency_buying_power: Decimal
    updated_at: datetime
    apex_starting_day_margin_equity: Optional[Decimal] = None
    buying_power_adjustment: Optional[Decimal] = None
    time_of_day: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def validate_price_effects(cls, data: Any) -> Any:
        if isinstance(data, dict):
            key = "unsettled-cryptocurrency-fiat-amount"
            effect = data.get("unsettled-cryptocurrency-fiat-effect")
            if effect == PriceEffect.DEBIT:
                data[key] = -abs(Decimal(data[key]))
        return _set_sign_for(data, ["pending_cash", "buying_power_adjustment"])


class AccountBalanceSnapshot(TastytradeJsonDataclass):
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
    time_of_day: Optional[str] = None
    long_cryptocurrency_value: Optional[Decimal] = None
    short_cryptocurrency_value: Optional[Decimal] = None
    cryptocurrency_margin_requirement: Optional[Decimal] = None
    unsettled_cryptocurrency_fiat_amount: Optional[Decimal] = None
    closed_loop_available_balance: Optional[Decimal] = None
    equity_offering_margin_requirement: Optional[Decimal] = None
    long_bond_value: Optional[Decimal] = None
    bond_margin_requirement: Optional[Decimal] = None

    @model_validator(mode="before")
    @classmethod
    def validate_price_effects(cls, data: Any) -> Any:
        if isinstance(data, dict):
            key = "unsettled-cryptocurrency-fiat-amount"
            effect = data.get("unsettled-cryptocurrency-fiat-effect")
            if effect == PriceEffect.DEBIT:
                data[key] = -abs(Decimal(data[key]))
        return _set_sign_for(data, ["pending_cash"])


class CurrentPosition(TastytradeJsonDataclass):
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
    mark: Optional[Decimal] = None
    mark_price: Optional[Decimal] = None
    restricted_quantity: Optional[Decimal] = None
    expires_at: Optional[datetime] = None
    fixing_price: Optional[Decimal] = None
    deliverable_type: Optional[str] = None
    average_yearly_market_close_price: Optional[Decimal] = None
    average_daily_market_close_price: Optional[Decimal] = None
    realized_day_gain_date: Optional[date] = None
    realized_today_date: Optional[date] = None

    @model_validator(mode="before")
    @classmethod
    def validate_price_effects(cls, data: Any) -> Any:
        return _set_sign_for(data, ["realized_day_gain", "realized_today"])


class FeesInfo(TastytradeJsonDataclass):
    total_fees: Decimal

    @model_validator(mode="before")
    @classmethod
    def validate_price_effects(cls, data: Any) -> Any:
        return _set_sign_for(data, ["total_fees"])


class Lot(TastytradeJsonDataclass):
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


class MarginReportEntry(TastytradeJsonDataclass):
    """
    Dataclass containing an individual entry (relating to a specific position)
    as part of the overall margin report.
    """

    description: str
    code: str
    buying_power: Decimal
    margin_calculation_type: str
    margin_requirement: Decimal
    expected_price_range_up_percent: Optional[Decimal] = None
    expected_price_range_down_percent: Optional[Decimal] = None
    groups: Optional[list[dict[str, Any]]] = None
    initial_requirement: Optional[Decimal] = None
    maintenance_requirement: Optional[Decimal] = None
    point_of_no_return_percent: Optional[Decimal] = None
    price_increase_percent: Optional[Decimal] = None
    price_decrease_percent: Optional[Decimal] = None
    underlying_symbol: Optional[str] = None
    underlying_type: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def validate_price_effects(cls, data: Any) -> Any:
        return _set_sign_for(
            data,
            [
                "buying_power",
                "margin_requirement",
                "initial_requirement",
                "maintenance_requirement",
            ],
        )


class MarginReport(TastytradeJsonDataclass):
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
    groups: list[Union[MarginReportEntry, EmptyDict]]
    initial_requirement: Optional[Decimal] = None

    @model_validator(mode="before")
    @classmethod
    def validate_price_effects(cls, data: Any) -> Any:
        return _set_sign_for(
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


class MarginRequirement(TastytradeJsonDataclass):
    """
    Dataclass containing general margin requirement information for a symbol.
    """

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


class PositionLimit(TastytradeJsonDataclass):
    """
    Dataclass containing information about general account limits.
    """

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
    is_portfolio_margin_enabled: Optional[bool] = None
    is_risk_reducing_only: Optional[bool] = None
    day_trade_count: Optional[int] = None
    autotrade_account_type: Optional[str] = None
    clearing_account_number: Optional[str] = None
    clearing_aggregation_identifier: Optional[str] = None
    is_cryptocurrency_closing_only: Optional[bool] = None
    pdt_reset_on: Optional[date] = None
    cmta_override: Optional[int] = None
    enhanced_fraud_safeguards_enabled_at: Optional[datetime] = None


class Transaction(TastytradeJsonDataclass):
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
    symbol: Optional[str] = None
    instrument_type: Optional[InstrumentType] = None
    underlying_symbol: Optional[str] = None
    action: Optional[OrderAction] = None
    quantity: Optional[Decimal] = None
    price: Optional[Decimal] = None
    regulatory_fees: Optional[Decimal] = None
    clearing_fees: Optional[Decimal] = None
    commission: Optional[Decimal] = None
    proprietary_index_option_fees: Optional[Decimal] = None
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
    other_charge_description: Optional[str] = None
    reverses_id: Optional[int] = None
    cost_basis_reconciliation_date: Optional[date] = None
    lots: Optional[list[Lot]] = None
    agency_price: Optional[Decimal] = None
    principal_price: Optional[Decimal] = None

    @model_validator(mode="before")
    @classmethod
    def validate_price_effects(cls, data: Any) -> Any:
        return _set_sign_for(
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


class Account(TastytradeJsonDataclass):
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
    day_trader_status: Union[str, bool]
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
    async def a_get_accounts(cls, session: Session, include_closed=False) -> list[Self]:
        """
        Gets all trading accounts associated with the Tastytrade user.

        :param session: the session to use for the request.
        :param include_closed:
            whether to include closed accounts in the results (default False)
        """
        data = await session._a_get("/customers/me/accounts")
        return [
            cls(**i["account"])
            for i in data["items"]
            if include_closed or not i["account"]["is-closed"]
        ]

    @classmethod
    def get_accounts(cls, session: Session, include_closed=False) -> list[Self]:
        """
        Gets all trading accounts associated with the Tastytrade user.

        :param session: the session to use for the request.
        :param include_closed:
            whether to include closed accounts in the results (default False)
        """
        data = session._get("/customers/me/accounts")
        return [
            cls(**i["account"])
            for i in data["items"]
            if include_closed or not i["account"]["is-closed"]
        ]

    @classmethod
    async def a_get_account(cls, session: Session, account_number: str) -> Self:
        """
        Returns the Tastytrade account associated with the given account ID.

        :param session: the session to use for the request.
        :param account_number: the account ID to get.
        """
        data = await session._a_get(f"/customers/me/accounts/{account_number}")
        return cls(**data)

    @classmethod
    def get_account(cls, session: Session, account_number: str) -> Self:
        """
        Returns the Tastytrade account associated with the given account ID.

        :param session: the session to use for the request.
        :param account_number: the account ID to get.
        """
        data = session._get(f"/customers/me/accounts/{account_number}")
        return cls(**data)

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

    async def a_get_balances(self, session: Session) -> AccountBalance:
        """
        Get the current balances of the account.

        :param session: the session to use for the request.
        """
        data = await session._a_get(f"/accounts/{self.account_number}/balances")
        return AccountBalance(**data)

    def get_balances(self, session: Session) -> AccountBalance:
        """
        Get the current balances of the account.

        :param session: the session to use for the request.
        """
        data = session._get(f"/accounts/{self.account_number}/balances")
        return AccountBalance(**data)

    async def a_get_balance_snapshots(
        self,
        session: Session,
        per_page: int = 250,
        page_offset: Optional[int] = None,
        currency: str = "USD",
        end_date: Optional[date] = None,
        start_date: Optional[date] = None,
        snapshot_date: Optional[date] = None,
        time_of_day: Literal["BOD", "EOD"] = "EOD",
    ) -> list[AccountBalanceSnapshot]:
        """
        Returns a list of balance snapshots. This list will
        just have a few snapshots if you don't pass a start
        date; otherwise, it will be each day's balances in
        the given range.

        :param session: the session to use for the request.
        :param currency: the currency to show balances in.
        :param start_date: the starting date of the range.
        :param end_date: the ending date of the range.
        :param snapshot_date: the date of the snapshot to get.
        :param time_of_day:
            the time of day of the snapshots to get, either 'EOD' (End Of Day) or 'BOD' (Beginning Of Day).
        """
        paginate = False
        if page_offset is None:
            page_offset = 0
            paginate = True
        params = {
            "per-page": per_page,
            "page-offset": page_offset,
            "currency": currency,
            "end-date": end_date,
            "start-date": start_date,
            "snapshot-date": snapshot_date,
            "time-of-day": time_of_day,
        }
        snapshots = []
        while True:
            response = await session.async_client.get(
                f"/accounts/{self.account_number}/balance-snapshots",
                params={
                    k: v  # type: ignore
                    for k, v in params.items()
                    if v is not None
                },
            )
            validate_response(response)
            json = response.json()
            snapshots.extend(
                [AccountBalanceSnapshot(**i) for i in json["data"]["items"]]
            )
            # handle pagination
            pagination = json["pagination"]
            if (
                pagination["page-offset"] >= pagination["total-pages"] - 1
                or not paginate
            ):
                break
            params["page-offset"] += 1  # type: ignore
        return snapshots

    def get_balance_snapshots(
        self,
        session: Session,
        per_page: int = 250,
        page_offset: Optional[int] = None,
        currency: str = "USD",
        end_date: Optional[date] = None,
        start_date: Optional[date] = None,
        snapshot_date: Optional[date] = None,
        time_of_day: Literal["BOD", "EOD"] = "EOD",
    ) -> list[AccountBalanceSnapshot]:
        """
        Returns a list of balance snapshots. This list will
        just have a few snapshots if you don't pass a start
        date; otherwise, it will be each day's balances in
        the given range.

        :param session: the session to use for the request.
        :param currency: the currency to show balances in.
        :param start_date: the starting date of the range.
        :param end_date: the ending date of the range.
        :param snapshot_date: the date of the snapshot to get.
        :param time_of_day:
            the time of day of the snapshots to get, either 'EOD' (End Of Day) or 'BOD' (Beginning Of Day).
        """
        paginate = False
        if page_offset is None:
            page_offset = 0
            paginate = True
        params = {
            "per-page": per_page,
            "page-offset": page_offset,
            "currency": currency,
            "end-date": end_date,
            "start-date": start_date,
            "snapshot-date": snapshot_date,
            "time-of-day": time_of_day,
        }
        snapshots = []
        while True:
            response = session.sync_client.get(
                f"/accounts/{self.account_number}/balance-snapshots",
                params={
                    k: v  # type: ignore
                    for k, v in params.items()
                    if v is not None
                },
            )
            validate_response(response)
            json = response.json()
            snapshots.extend(
                [AccountBalanceSnapshot(**i) for i in json["data"]["items"]]
            )
            # handle pagination
            pagination = json["pagination"]
            if (
                pagination["page-offset"] >= pagination["total-pages"] - 1
                or not paginate
            ):
                break
            params["page-offset"] += 1  # type: ignore
        return snapshots

    async def a_get_positions(
        self,
        session: Session,
        underlying_symbols: Optional[list[str]] = None,
        symbol: Optional[str] = None,
        instrument_type: Optional[InstrumentType] = None,
        include_closed: Optional[bool] = None,
        underlying_product_code: Optional[str] = None,
        partition_keys: Optional[list[str]] = None,
        net_positions: Optional[bool] = None,
        include_marks: Optional[bool] = None,
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
        underlying_symbols: Optional[list[str]] = None,
        symbol: Optional[str] = None,
        instrument_type: Optional[InstrumentType] = None,
        include_closed: Optional[bool] = None,
        underlying_product_code: Optional[str] = None,
        partition_keys: Optional[list[str]] = None,
        net_positions: Optional[bool] = None,
        include_marks: Optional[bool] = None,
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
        page_offset: Optional[int] = None,
        sort: str = "Desc",
        type: Optional[str] = None,
        types: Optional[list[str]] = None,
        sub_types: Optional[list[str]] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        instrument_type: Optional[InstrumentType] = None,
        symbol: Optional[str] = None,
        underlying_symbol: Optional[str] = None,
        action: Optional[str] = None,
        partition_key: Optional[str] = None,
        futures_symbol: Optional[str] = None,
        start_at: Optional[datetime] = None,
        end_at: Optional[datetime] = None,
    ) -> list[Transaction]:
        """
        Get transaction history of the account.

        :param session: the session to use for the request.
        :param per_page: the number of results to return per page.
        :param page_offset:
            provide a specific page to get; if not provided, get all pages
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
        # if a specific page is provided, we just get that page;
        # otherwise, we loop through all pages
        paginate = False
        if page_offset is None:
            page_offset = 0
            paginate = True
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
        # loop through pages and get all transactions
        txns = []
        while True:
            response = await session.async_client.get(
                f"/accounts/{self.account_number}/transactions",
                params={
                    k: v  # type: ignore
                    for k, v in params.items()
                    if v is not None
                },
            )
            validate_response(response)
            json = response.json()
            txns.extend([Transaction(**i) for i in json["data"]["items"]])
            # handle pagination
            pagination = json["pagination"]
            if (
                pagination["page-offset"] >= pagination["total-pages"] - 1
                or not paginate
            ):
                break
            params["page-offset"] += 1  # type: ignore

        return txns

    def get_history(
        self,
        session: Session,
        per_page: int = 250,
        page_offset: Optional[int] = None,
        sort: str = "Desc",
        type: Optional[str] = None,
        types: Optional[list[str]] = None,
        sub_types: Optional[list[str]] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        instrument_type: Optional[InstrumentType] = None,
        symbol: Optional[str] = None,
        underlying_symbol: Optional[str] = None,
        action: Optional[str] = None,
        partition_key: Optional[str] = None,
        futures_symbol: Optional[str] = None,
        start_at: Optional[datetime] = None,
        end_at: Optional[datetime] = None,
    ) -> list[Transaction]:
        """
        Get transaction history of the account.

        :param session: the session to use for the request.
        :param per_page: the number of results to return per page.
        :param page_offset:
            provide a specific page to get; if not provided, get all pages
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
        # if a specific page is provided, we just get that page;
        # otherwise, we loop through all pages
        paginate = False
        if page_offset is None:
            page_offset = 0
            paginate = True
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
        # loop through pages and get all transactions
        txns = []
        while True:
            response = session.sync_client.get(
                f"/accounts/{self.account_number}/transactions",
                params={
                    k: v  # type: ignore
                    for k, v in params.items()
                    if v is not None
                },
            )
            validate_response(response)
            json = response.json()
            txns.extend([Transaction(**i) for i in json["data"]["items"]])
            # handle pagination
            pagination = json["pagination"]
            if (
                pagination["page-offset"] >= pagination["total-pages"] - 1
                or not paginate
            ):
                break
            params["page-offset"] += 1  # type: ignore

        return txns

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
        self, session: Session, day: Optional[date] = None
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

    def get_total_fees(self, session: Session, day: Optional[date] = None) -> FeesInfo:
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
        time_back: Optional[str] = None,
        start_time: Optional[datetime] = None,
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
        time_back: Optional[str] = None,
        start_time: Optional[datetime] = None,
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

    async def a_get_position_limit(self, session: Session) -> PositionLimit:
        """
        Get the maximum order size information for the account.

        :param session: the session to use for the request.
        """
        data = await session._a_get(f"/accounts/{self.account_number}/position-limit")
        return PositionLimit(**data)

    def get_position_limit(self, session: Session) -> PositionLimit:
        """
        Get the maximum order size information for the account.

        :param session: the session to use for the request.
        """
        data = session._get(f"/accounts/{self.account_number}/position-limit")
        return PositionLimit(**data)

    async def a_get_effective_margin_requirements(
        self, session: Session, symbol: str
    ) -> MarginRequirement:
        """
        Get the effective margin requirements for a given symbol.

        :param session:
            the session to use for the request, can't be certification
        :param symbol: the symbol to get margin requirements for.
        """
        if symbol:
            symbol = symbol.replace("/", "%2F")
        data = await session._a_get(
            f"/accounts/{self.account_number}/margin-"
            f"requirements/{symbol}/effective"
        )
        return MarginRequirement(**data)

    def get_effective_margin_requirements(
        self, session: Session, symbol: str
    ) -> MarginRequirement:
        """
        Get the effective margin requirements for a given symbol.

        :param session:
            the session to use for the request, can't be certification
        :param symbol: the symbol to get margin requirements for.
        """
        if symbol:
            symbol = symbol.replace("/", "%2F")
        data = session._get(
            f"/accounts/{self.account_number}/margin-"
            f"requirements/{symbol}/effective"
        )
        return MarginRequirement(**data)

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
        page_offset: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        underlying_symbol: Optional[str] = None,
        statuses: Optional[list[OrderStatus]] = None,
        futures_symbol: Optional[str] = None,
        underlying_instrument_type: Optional[InstrumentType] = None,
        sort: Optional[str] = None,
        start_at: Optional[datetime] = None,
        end_at: Optional[datetime] = None,
    ) -> list[PlacedOrder]:
        """
        Get order history of the account.

        :param session: the session to use for the request.
        :param per_page: the number of results to return per page.
        :param page_offset:
            provide a specific page to get; if not provided, get all pages
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
        # if a specific page is provided, we just get that page;
        # otherwise, we loop through all pages
        paginate = False
        if page_offset is None:
            page_offset = 0
            paginate = True
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
        # loop through pages and get all transactions
        orders = []
        while True:
            response = await session.async_client.get(
                f"/accounts/{self.account_number}/orders",
                params={
                    k: v  # type: ignore
                    for k, v in params.items()
                    if v is not None
                },
            )
            validate_response(response)
            json = response.json()
            orders.extend([PlacedOrder(**i) for i in json["data"]["items"]])
            # handle pagination
            pagination = json["pagination"]
            if (
                pagination["page-offset"] >= pagination["total-pages"] - 1
                or not paginate
            ):
                break
            params["page-offset"] += 1  # type: ignore

        return orders

    def get_order_history(
        self,
        session: Session,
        per_page: int = 50,
        page_offset: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        underlying_symbol: Optional[str] = None,
        statuses: Optional[list[OrderStatus]] = None,
        futures_symbol: Optional[str] = None,
        underlying_instrument_type: Optional[InstrumentType] = None,
        sort: Optional[str] = None,
        start_at: Optional[datetime] = None,
        end_at: Optional[datetime] = None,
    ) -> list[PlacedOrder]:
        """
        Get order history of the account.

        :param session: the session to use for the request.
        :param per_page: the number of results to return per page.
        :param page_offset:
            provide a specific page to get; if not provided, get all pages
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
        # if a specific page is provided, we just get that page;
        # otherwise, we loop through all pages
        paginate = False
        if page_offset is None:
            page_offset = 0
            paginate = True
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
        # loop through pages and get all transactions
        orders = []
        while True:
            response = session.sync_client.get(
                f"/accounts/{self.account_number}/orders",
                params={
                    k: v  # type: ignore
                    for k, v in params.items()
                    if v is not None
                },
            )
            validate_response(response)
            json = response.json()
            orders.extend([PlacedOrder(**i) for i in json["data"]["items"]])
            # handle pagination
            pagination = json["pagination"]
            if (
                pagination["page-offset"] >= pagination["total-pages"] - 1
                or not paginate
            ):
                break
            params["page-offset"] += 1  # type: ignore

        return orders

    async def a_get_complex_order_history(
        self, session: Session, per_page: int = 50, page_offset: Optional[int] = None
    ) -> list[PlacedComplexOrder]:
        """
        Get order history of the account.

        :param session: the session to use for the request.
        :param per_page: the number of results to return per page.
        :param page_offset:
            provide a specific page to get; if not provided, get all pages
        """
        # if a specific page is provided, we just get that page;
        # otherwise, we loop through all pages
        paginate = False
        if page_offset is None:
            page_offset = 0
            paginate = True
        params = {"per-page": per_page, "page-offset": page_offset}
        # loop through pages and get all transactions
        orders = []
        while True:
            response = await session.async_client.get(
                f"/accounts/{self.account_number}/complex-orders",
                params={k: v for k, v in params.items() if v is not None},
            )
            validate_response(response)
            json = response.json()
            orders.extend([PlacedComplexOrder(**i) for i in json["data"]["items"]])
            # handle pagination
            pagination = json["pagination"]
            if (
                pagination["page-offset"] >= pagination["total-pages"] - 1
                or not paginate
            ):
                break
            params["page-offset"] += 1  # type: ignore

        return orders

    def get_complex_order_history(
        self, session: Session, per_page: int = 50, page_offset: Optional[int] = None
    ) -> list[PlacedComplexOrder]:
        """
        Get order history of the account.

        :param session: the session to use for the request.
        :param per_page: the number of results to return per page.
        :param page_offset:
            provide a specific page to get; if not provided, get all pages
        """
        # if a specific page is provided, we just get that page;
        # otherwise, we loop through all pages
        paginate = False
        if page_offset is None:
            page_offset = 0
            paginate = True
        params = {"per-page": per_page, "page-offset": page_offset}
        # loop through pages and get all transactions
        orders = []
        while True:
            response = session.sync_client.get(
                f"/accounts/{self.account_number}/complex-orders",
                params={k: v for k, v in params.items() if v is not None},
            )
            validate_response(response)
            json = response.json()
            orders.extend([PlacedComplexOrder(**i) for i in json["data"]["items"]])
            # handle pagination
            pagination = json["pagination"]
            if (
                pagination["page-offset"] >= pagination["total-pages"] - 1
                or not paginate
            ):
                break
            params["page-offset"] += 1  # type: ignore

        return orders

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

    async def a_get_order_chains(
        self,
        session: Session,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
    ) -> list[OrderChain]:
        """
        Get a list of order chains (open + rolls + close) for given symbol
        over the given time frame, with total P/L, commissions, etc.

        :param session: the session to use for the request.
        :param symbol: the underlying symbol for the chains.
        :param start_time: the beginning time of the query.
        :param end_time: the ending time of the query.
        """
        params = {
            "account-numbers[]": self.account_number,
            "underlying-symbols[]": symbol,
            "start-at": start_time.strftime(TT_DATE_FMT),
            "end-at": end_time.strftime(TT_DATE_FMT),
            "defer-open-winner-loser-filtering-to-frontend": False,
            "per-page": 250,
        }
        headers = {
            "Authorization": session.session_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{VAST_URL}/order-chains",
                headers=headers,
                params=params,
            )
            validate_response(response)
            chains = response.json()["data"]["items"]
            return [OrderChain(**i) for i in chains]

    def get_order_chains(
        self,
        session: Session,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
    ) -> list[OrderChain]:
        """
        Get a list of order chains (open + rolls + close) for given symbol
        over the given time frame, with total P/L, commissions, etc.

        :param session: the session to use for the request.
        :param symbol: the underlying symbol for the chains.
        :param start_time: the beginning time of the query.
        :param end_time: the ending time of the query.
        """
        params = {
            "account-numbers[]": self.account_number,
            "underlying-symbols[]": symbol,
            "start-at": start_time.strftime(TT_DATE_FMT),
            "end-at": end_time.strftime(TT_DATE_FMT),
            "defer-open-winner-loser-filtering-to-frontend": False,
            "per-page": 250,
        }
        headers = {
            "Authorization": session.session_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        response = httpx.get(
            f"{VAST_URL}/order-chains",
            headers=headers,
            params=params,
        )
        validate_response(response)
        chains = response.json()["data"]["items"]
        return [OrderChain(**i) for i in chains]
