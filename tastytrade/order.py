from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import ConfigDict, computed_field, field_serializer, model_validator

from tastytrade import version_str
from tastytrade.utils import (
    PriceEffect,
    TastytradeData,
    get_sign,
    set_sign_for,
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


class FillInfo(TastytradeData):
    """
    Dataclass that contains information about an order fill.
    """

    fill_id: str
    quantity: Decimal
    fill_price: Decimal
    filled_at: datetime
    destination_venue: str | None = None
    ext_group_fill_id: str | None = None
    ext_exec_id: str | None = None


class Leg(TastytradeData):
    """
    Dataclass that represents an order leg.

    Classes that inherit from :class:`TradeableTastytradeData` can
    call :meth:`build_leg` to build a leg from the dataclass.
    """

    instrument_type: InstrumentType
    symbol: str
    action: OrderAction
    quantity: Decimal | int | None = None
    remaining_quantity: Decimal | None = None
    fills: list[FillInfo] | None = None


class TradeableTastytradeData(TastytradeData):
    """
    Dataclass that represents a tradeable instrument.

    Classes that inherit from this class can call :meth:`build_leg` to build a
    leg from the dataclass.
    """

    instrument_type: InstrumentType
    symbol: str

    def build_leg(self, quantity: Decimal | int | None, action: OrderAction) -> Leg:
        """
        Builds an order :class:`Leg` from the dataclass.

        :param quantity:
            the quantity of the symbol to trade, set this as `None` for notional orders
        :param action: :class:`OrderAction` to perform, e.g. BUY_TO_OPEN
        """
        return Leg(
            instrument_type=self.instrument_type,
            symbol=self.symbol,
            quantity=quantity,
            action=action,
        )


class Message(TastytradeData):
    """
    Dataclass that represents a message from the Tastytrade API, usually
    a warning or an error.
    """

    code: str
    message: str
    preflight_id: str | None = None

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


class OrderConditionPriceComponent(TastytradeData):
    """
    Dataclass that represents a price component of an order condition.
    """

    symbol: str
    instrument_type: InstrumentType
    quantity: Decimal
    quantity_direction: str


class OrderCondition(TastytradeData):
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


class OrderRule(TastytradeData):
    """
    Dataclass that represents an order rule for a complex order.
    """

    route_after: datetime
    routed_at: datetime
    cancel_at: datetime
    cancelled_at: datetime
    order_conditions: list[OrderCondition]


class AdvancedInstructions(TastytradeData):
    """
    Dataclass containing advanced order rules.
    """

    #: By default, if a position meant to be closed by a closing order is no longer
    #: open, the API will turn it into an opening order. With this flag, the API would
    #: instead discard the closing order.
    strict_position_effect_validation: bool = False


class NewOrder(TastytradeData):
    """
    Dataclass containing information about a new order. Also used for
    modifying existing orders.
    """

    model_config = ConfigDict(extra="allow")

    time_in_force: OrderTimeInForce
    order_type: OrderType
    source: str = version_str
    legs: list[Leg]
    gtc_date: date | None = None
    #: For a stop/stop limit order. If the latter, use price for the limit price
    stop_trigger: Decimal | None = None
    #: The price of the order; negative = debit, positive = credit
    price: Decimal | None = None
    #: The actual notional value of the order. Only for notional market orders!
    value: Decimal | None = None
    partition_key: str | None = None
    preflight_id: str | None = None
    rules: OrderRule | None = None
    advanced_instructions: AdvancedInstructions | None = None
    #: External identifier for the order, used to track orders across systems
    external_identifier: str | None = None

    @computed_field  # type: ignore[misc]
    @property
    def price_effect(self) -> PriceEffect | None:
        return get_sign(self.price)

    @computed_field  # type: ignore[misc]
    @property
    def value_effect(self) -> PriceEffect | None:
        return get_sign(self.value)

    @field_serializer("price", "value")
    def serialize_fields(self, field: Decimal | None) -> Decimal | None:
        return abs(field) if field else None


class NewComplexOrder(TastytradeData):
    """
    Dataclass containing information about a new OTOCO order.
    Also used for modifying existing orders.
    """

    orders: list[NewOrder]
    source: str = version_str
    trigger_order: NewOrder | None = None
    type: ComplexOrderType = ComplexOrderType.OCO

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        if self.trigger_order is not None:
            self.type = ComplexOrderType.OTOCO


class PlacedOrder(TastytradeData):
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
    size: Decimal | None = None
    price: Decimal | None = None
    gtc_date: date | None = None
    value: Decimal | None = None
    stop_trigger: str | None = None
    contingent_status: str | None = None
    confirmation_status: str | None = None
    cancelled_at: datetime | None = None
    cancel_user_id: str | None = None
    cancel_username: str | None = None
    replacing_order_id: int | None = None
    replaces_order_id: int | None = None
    in_flight_at: datetime | None = None
    live_at: datetime | None = None
    received_at: datetime | None = None
    reject_reason: str | None = None
    user_id: str | None = None
    username: str | None = None
    terminal_at: datetime | None = None
    complex_order_id: str | int | None = None
    complex_order_tag: str | None = None
    preflight_id: str | int | None = None
    order_rule: OrderRule | None = None
    source: str | None = None
    #: External identifier for the order, used to track orders across systems
    external_identifier: str | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_price_effects(cls, data: Any) -> Any:
        return set_sign_for(data, ["price", "value"])


class PlacedComplexOrder(TastytradeData):
    """
    Dataclass containing information about an already placed complex order.
    """

    account_number: str
    type: str
    orders: list[PlacedOrder]
    #: the ID of the order; test orders placed with dry_run don't have an ID
    id: int = -1
    trigger_order: PlacedOrder | None = None
    terminal_at: str | None = None
    ratio_price_threshold: Decimal | None = None
    ratio_price_comparator: str | None = None
    ratio_price_is_threshold_based_on_notional: bool | None = None
    related_orders: list[dict[str, str]] | None = None


class BuyingPowerEffect(TastytradeData):
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
        return set_sign_for(
            data,
            [
                "change_in_margin_requirement",
                "change_in_buying_power",
                "current_buying_power",
                "new_buying_power",
                "isolated_order_margin_requirement",
            ],
        )


class FeeCalculation(TastytradeData):
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
        return set_sign_for(
            data,
            [
                "regulatory_fees",
                "clearing_fees",
                "commission",
                "proprietary_index_option_fees",
                "total_fees",
            ],
        )


class PlacedComplexOrderResponse(TastytradeData):
    """
    Dataclass grouping together information about a placed complex order.
    """

    buying_power_effect: BuyingPowerEffect
    complex_order: PlacedComplexOrder
    fee_calculation: FeeCalculation | None = None
    warnings: list[Message] | None = None
    errors: list[Message] | None = None


class PlacedOrderResponse(TastytradeData):
    """
    Dataclass grouping together information about a placed order.
    """

    buying_power_effect: BuyingPowerEffect
    order: PlacedOrder
    fee_calculation: FeeCalculation | None = None
    warnings: list[Message] | None = None
    errors: list[Message] | None = None
