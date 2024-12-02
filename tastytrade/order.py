from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional, Union

from pydantic import computed_field, field_serializer, model_validator

from tastytrade import VERSION
from tastytrade.utils import (
    PriceEffect,
    TastytradeJsonDataclass,
    _get_sign,
    _set_sign_for,
)


class InstrumentType(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the valid types of instruments
    and their representation in the API.
    """

    BOND = "Bond"
    CRYPTOCURRENCY = "Cryptocurrency"
    CURRENCY_PAIR = "Currency Pair"
    EQUITY = "Equity"
    EQUITY_OFFERING = "Equity Offering"
    EQUITY_OPTION = "Equity Option"
    FIXED_INCOME = "Fixed Income Security"
    FUTURE = "Future"
    FUTURE_OPTION = "Future Option"
    INDEX = "Index"
    LIQUIDITY_POOL = "Liquidity Pool"
    UNKNOWN = "Unknown"
    WARRANT = "Warrant"


class OrderAction(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the valid order actions.
    """

    BUY_TO_OPEN = "Buy to Open"
    BUY_TO_CLOSE = "Buy to Close"
    SELL_TO_OPEN = "Sell to Open"
    SELL_TO_CLOSE = "Sell to Close"
    #: for futures only
    BUY = "Buy"
    #: for futures only
    SELL = "Sell"


class OrderStatus(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains different order statuses.
    A typical (successful) order follows a progression:

    RECEIVED -> LIVE -> FILLED
    """

    RECEIVED = "Received"
    CANCELLED = "Cancelled"
    FILLED = "Filled"
    EXPIRED = "Expired"
    LIVE = "Live"
    REJECTED = "Rejected"
    CONTINGENT = "Contingent"
    ROUTED = "Routed"
    IN_FLIGHT = "In Flight"
    CANCEL_REQUESTED = "Cancel Requested"
    REPLACE_REQUESTED = "Replace Requested"
    REMOVED = "Removed"
    PARTIALLY_REMOVED = "Partially Removed"


class OrderTimeInForce(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the valid TIFs for orders.
    """

    DAY = "Day"
    GTC = "GTC"
    GTD = "GTD"
    EXT = "Ext"
    GTC_EXT = "GTC Ext"
    IOC = "IOC"


class OrderType(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the valid types of orders.
    """

    LIMIT = "Limit"
    MARKET = "Market"
    MARKETABLE_LIMIT = "Marketable Limit"
    STOP = "Stop"
    STOP_LIMIT = "Stop Limit"
    NOTIONAL_MARKET = "Notional Market"


class ComplexOrderType(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the valid complex order types.
    """

    OCO = "OCO"
    OTOCO = "OTOCO"


class FillInfo(TastytradeJsonDataclass):
    """
    Dataclass that contains information about an order fill.
    """

    fill_id: str
    quantity: Decimal
    fill_price: Decimal
    filled_at: datetime
    destination_venue: Optional[str] = None
    ext_group_fill_id: Optional[str] = None
    ext_exec_id: Optional[str] = None


class Leg(TastytradeJsonDataclass):
    """
    Dataclass that represents an order leg.

    Classes that inherit from :class:`TradeableTastytradeJsonDataclass` can
    call :meth:`build_leg` to build a leg from the dataclass.
    """

    instrument_type: InstrumentType
    symbol: str
    action: OrderAction
    quantity: Optional[Decimal] = None
    remaining_quantity: Optional[Decimal] = None
    fills: Optional[list[FillInfo]] = None


class TradeableTastytradeJsonDataclass(TastytradeJsonDataclass):
    """
    Dataclass that represents a tradeable instrument.

    Classes that inherit from this class can call :meth:`build_leg` to build a
    leg from the dataclass.
    """

    instrument_type: InstrumentType
    symbol: str

    def build_leg(self, quantity: Decimal, action: OrderAction) -> Leg:
        """
        Builds an order :class:`Leg` from the dataclass.

        :param quantity: the quantity of the symbol to trade
        :param action: :class:`OrderAction` to perform, e.g. BUY_TO_OPEN

        :return: a :class:`Leg` object
        """
        return Leg(
            instrument_type=self.instrument_type,
            symbol=self.symbol,
            quantity=quantity,
            action=action,
        )


class Message(TastytradeJsonDataclass):
    """
    Dataclass that represents a message from the Tastytrade API, usually
    a warning or an error.
    """

    code: str
    message: str
    preflight_id: Optional[str] = None

    def __str__(self):
        return f"{self.code}: {self.message}"


class OrderConditionPriceComponent(TastytradeJsonDataclass):
    """
    Dataclass that represents a price component of an order condition.
    """

    symbol: str
    instrument_type: InstrumentType
    quantity: Decimal
    quantity_direction: str


class OrderCondition(TastytradeJsonDataclass):
    """
    Dataclass that represents an order condition for an order rule.
    """

    id: str
    action: str
    symbol: str
    instrument_type: InstrumentType
    indicator: str
    comparator: str
    threshold: Decimal
    is_threshold_based_on_notional: bool
    triggered_at: datetime
    triggered_value: Decimal
    price_components: list[OrderConditionPriceComponent]


class OrderRule(TastytradeJsonDataclass):
    """
    Dataclass that represents an order rule for a complex order.
    """

    route_after: datetime
    routed_at: datetime
    cancel_at: datetime
    cancelled_at: datetime
    order_conditions: list[OrderCondition]


class NewOrder(TastytradeJsonDataclass):
    """
    Dataclass containing information about a new order. Also used for
    modifying existing orders.
    """

    time_in_force: OrderTimeInForce
    order_type: OrderType
    source: str = f"tastyware/tastytrade:v{VERSION}"
    legs: list[Leg]
    gtc_date: Optional[date] = None
    #: For a stop/stop limit order. If the latter, use price for the limit price
    stop_trigger: Optional[Decimal] = None
    #: The price of the order; negative = debit, positive = credit
    price: Optional[Decimal] = None
    #: The actual notional value of the order. Only for notional market orders!
    value: Optional[Decimal] = None
    partition_key: Optional[str] = None
    preflight_id: Optional[str] = None
    rules: Optional[OrderRule] = None

    @computed_field
    @property
    def price_effect(self) -> Optional[PriceEffect]:
        return _get_sign(self.price)

    @computed_field
    @property
    def value_effect(self) -> Optional[PriceEffect]:
        return _get_sign(self.value)

    @field_serializer("price", "value")
    def serialize_fields(self, field: Optional[Decimal]) -> Optional[Decimal]:
        return abs(field) if field else None


class NewComplexOrder(TastytradeJsonDataclass):
    """
    Dataclass containing information about a new OTOCO order.
    Also used for modifying existing orders.
    """

    orders: list[NewOrder]
    source: str = f"tastyware/tastytrade:v{VERSION}"
    trigger_order: Optional[NewOrder] = None
    type: ComplexOrderType = ComplexOrderType.OCO

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.trigger_order is not None:
            self.type = ComplexOrderType.OTOCO


class PlacedOrder(TastytradeJsonDataclass):
    """
    Dataclass containing information about an existing order, whether it's
    been filled or not.
    """

    account_number: str
    time_in_force: OrderTimeInForce
    order_type: OrderType
    underlying_symbol: str
    underlying_instrument_type: InstrumentType
    status: OrderStatus
    cancellable: bool
    editable: bool
    edited: bool
    updated_at: datetime
    legs: list[Leg]
    #: the ID of the order; test orders placed with dry_run don't have an ID
    id: int = -1
    size: Optional[Decimal] = None
    price: Optional[Decimal] = None
    gtc_date: Optional[date] = None
    value: Optional[Decimal] = None
    stop_trigger: Optional[str] = None
    contingent_status: Optional[str] = None
    confirmation_status: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    cancel_user_id: Optional[str] = None
    cancel_username: Optional[str] = None
    replacing_order_id: Optional[str] = None
    replaces_order_id: Optional[str] = None
    in_flight_at: Optional[datetime] = None
    live_at: Optional[datetime] = None
    received_at: Optional[datetime] = None
    reject_reason: Optional[str] = None
    user_id: Optional[str] = None
    username: Optional[str] = None
    terminal_at: Optional[datetime] = None
    complex_order_id: Optional[Union[str, int]] = None
    complex_order_tag: Optional[str] = None
    preflight_id: Optional[Union[str, int]] = None
    order_rule: Optional[OrderRule] = None

    @model_validator(mode="before")
    @classmethod
    def validate_price_effects(cls, data: Any) -> Any:
        return _set_sign_for(data, ["price", "value"])


class PlacedComplexOrder(TastytradeJsonDataclass):
    """
    Dataclass containing information about an already placed complex order.
    """

    account_number: str
    type: str
    orders: list[PlacedOrder]
    #: the ID of the order; test orders placed with dry_run don't have an ID
    id: int = -1
    trigger_order: Optional[PlacedOrder] = None
    terminal_at: Optional[str] = None
    ratio_price_threshold: Optional[Decimal] = None
    ratio_price_comparator: Optional[str] = None
    ratio_price_is_threshold_based_on_notional: Optional[bool] = None
    related_orders: Optional[list[dict[str, str]]] = None


class BuyingPowerEffect(TastytradeJsonDataclass):
    """
    Dataclass containing information about the effect of a trade on buying
    power.
    """

    change_in_margin_requirement: Decimal
    change_in_buying_power: Decimal
    current_buying_power: Decimal
    new_buying_power: Decimal
    isolated_order_margin_requirement: Decimal
    is_spread: bool
    impact: Decimal
    effect: PriceEffect

    @model_validator(mode="before")
    @classmethod
    def validate_price_effects(cls, data: Any) -> Any:
        return _set_sign_for(
            data,
            [
                "change_in_margin_requirement",
                "change_in_buying_power",
                "current_buying_power",
                "new_buying_power",
                "isolated_order_margin_requirement",
            ],
        )


class FeeCalculation(TastytradeJsonDataclass):
    """
    Dataclass containing information about the fees associated with a trade.
    """

    regulatory_fees: Decimal
    clearing_fees: Decimal
    commission: Decimal
    proprietary_index_option_fees: Decimal
    total_fees: Decimal

    @model_validator(mode="before")
    @classmethod
    def validate_price_effects(cls, data: Any) -> Any:
        return _set_sign_for(
            data,
            [
                "regulatory_fees",
                "clearing_fees",
                "commission",
                "proprietary_index_option_fees",
                "total_fees",
            ],
        )


class PlacedComplexOrderResponse(TastytradeJsonDataclass):
    """
    Dataclass grouping together information about a placed complex order.
    """

    buying_power_effect: BuyingPowerEffect
    complex_order: PlacedComplexOrder
    fee_calculation: Optional[FeeCalculation] = None
    warnings: Optional[list[Message]] = None
    errors: Optional[list[Message]] = None


class PlacedOrderResponse(TastytradeJsonDataclass):
    """
    Dataclass grouping together information about a placed order.
    """

    buying_power_effect: BuyingPowerEffect
    order: PlacedOrder
    fee_calculation: Optional[FeeCalculation] = None
    warnings: Optional[list[Message]] = None
    errors: Optional[list[Message]] = None


class OrderChainEntry(TastytradeJsonDataclass):
    """
    Dataclass containing information about a single order in an order chain.
    """

    symbol: str
    instrument_type: InstrumentType
    quantity: str
    quantity_type: str
    quantity_numeric: Decimal


class OrderChainLeg(TastytradeJsonDataclass):
    """
    Dataclass containing information about a single leg in an order
    from an order chain.
    """

    symbol: str
    instrument_type: InstrumentType
    action: OrderAction
    fill_quantity: Decimal
    order_quantity: Decimal


class OrderChainNode(TastytradeJsonDataclass):
    """
    Dataclass containing information about a single node in an order chain.
    """

    node_type: str
    id: str
    description: str
    occurred_at: Optional[datetime] = None
    total_fees: Optional[Decimal] = None
    total_fill_cost: Optional[Decimal] = None
    gcd_quantity: Optional[Decimal] = None
    fill_cost_per_quantity: Optional[Decimal] = None
    order_fill_count: Optional[int] = None
    roll: Optional[bool] = None
    legs: Optional[list[OrderChainLeg]] = None
    entries: Optional[list[OrderChainEntry]] = None

    @model_validator(mode="before")
    @classmethod
    def validate_price_effects(cls, data: Any) -> Any:
        return _set_sign_for(
            data,
            [
                "total_fees",
                "total_fill_cost",
                "fill_cost_per_quantity",
            ],
        )


class ComputedData(TastytradeJsonDataclass):
    """
    Dataclass containing computed data about an order chain.
    """

    open: bool
    updated_at: datetime
    total_fees: Decimal
    total_commissions: Decimal
    realized_gain: Decimal
    realized_gain_with_fees: Decimal
    winner_realized_and_closed: bool
    winner_realized: bool
    winner_realized_with_fees: bool
    roll_count: int
    opened_at: datetime
    last_occurred_at: datetime
    started_at_days_to_expiration: int
    duration: int
    total_opening_cost: Decimal
    total_closing_cost: Decimal
    total_cost: Decimal
    gcd_open_quantity: Decimal
    fees_missing: bool
    open_entries: list[OrderChainEntry]
    total_cost_per_unit: Optional[Decimal] = None

    @model_validator(mode="before")
    @classmethod
    def validate_price_effects(cls, data: Any) -> Any:
        return _set_sign_for(
            data,
            [
                "total_fees",
                "total_commissions",
                "realized_gain",
                "realized_gain_with_fees",
                "total_opening_cost",
                "total_closing_cost",
                "total_cost",
                "total_cost_per_unit",
            ],
        )


class OrderChain(TastytradeJsonDataclass):
    """
    Dataclass containing information about an order chain: a group of orders
    for a specific underlying, such as total P/L, rolls, current P/L in a
    symbol, etc.
    """

    id: int
    account_number: str
    description: str
    underlying_symbol: str
    computed_data: ComputedData
    lite_nodes: list[OrderChainNode]
    lite_nodes_sizes: Optional[int] = None
    updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
