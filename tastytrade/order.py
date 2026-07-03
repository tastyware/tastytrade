import math
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import StrEnum
from functools import cached_property
from typing import Any, Generic, Literal, TypeVar

from pydantic import (
    Field,
    SerializerFunctionWrapHandler,
    computed_field,
    model_serializer,
    model_validator,
)
from typing_extensions import deprecated

from tastytrade import version_str
from tastytrade.utils import (
    PriceEffect,
    TastytradeData,
    TastytradeError,
    get_sign,
    set_sign_for,
)


class InstrumentType(StrEnum):
    """
    Contains the valid types of instruments and their representation in the API.
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


class OrderAction(StrEnum):
    """
    Contains the valid order actions.
    """

    BUY_TO_OPEN = "Buy to Open"
    BUY_TO_CLOSE = "Buy to Close"
    SELL_TO_OPEN = "Sell to Open"
    SELL_TO_CLOSE = "Sell to Close"
    #: for futures only
    BUY = "Buy"
    #: for futures only
    SELL = "Sell"

    @property
    def multiplier(self) -> int:
        return -1 if "Sell" in self.value else 1


class OrderStatus(StrEnum):
    """
    Contains different order statuses.
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


class OrderTimeInForce(StrEnum):
    """
    Contains the valid TIFs for orders.
    """

    DAY = "Day"
    GTC = "GTC"
    GTD = "GTD"
    EXT = "Ext"
    OVERNIGHT = "Ext Overnight"
    GTC_EXT = "GTC Ext"
    GTC_OVERNIGHT = "GTC Ext Overnight"
    IOC = "IOC"


class OrderType(StrEnum):
    """
    Contains the valid types of orders.
    """

    LIMIT = "Limit"
    MARKET = "Market"
    MARKETABLE_LIMIT = "Marketable Limit"
    STOP = "Stop"
    STOP_LIMIT = "Stop Limit"
    NOTIONAL_MARKET = "Notional Market"


class ComplexOrderType(StrEnum):
    """
    Contains the valid complex order types.
    """

    OCO = "OCO"
    OTOCO = "OTOCO"
    OTO = "OTO"
    PAIRS = "PAIRS"


class FillBehavior(StrEnum):
    """
    Valid fill behaviors in the paper environment.
    """

    #: fill after :attr:`NewOrder.delay` seconds
    DELAYED = "delayed"
    #: fill immediately
    IMMEDIATE = "immediate"
    #: never fill
    NEVER = "never"
    #: fill at given :attr:`NewOrder.schedule`
    SCHEDULED = "scheduled"
    #: reject order immediately
    REJECT = "reject"
    #: fill half immediately, the other half after 1 second
    PARTIAL = "partial"


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

    @property
    def multiplier(self) -> Decimal | int:
        if self.quantity is None:
            raise TastytradeError(
                "Can't calculate multiplier for legs without a quantity!"
            )
        return self.action.multiplier * self.quantity


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
            the quantity of the symbol to trade, set this as ``None`` for notional
            orders
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


class BaseOrder(TastytradeData):
    """
    Base class for different kinds of orders. For internal use.
    """

    time_in_force: OrderTimeInForce = OrderTimeInForce.DAY
    source: str = version_str
    legs: list[Leg]
    gtc_date: date | None = None
    partition_key: str | None = None
    preflight_id: str | None = None
    rules: OrderRule | None = None
    advanced_instructions: AdvancedInstructions | None = None
    #: External identifier for the order, used to track orders across systems
    external_identifier: str | None = None
    #: controls when/if/how fill happens on the paper API
    behavior: FillBehavior = FillBehavior.IMMEDIATE
    #: specific time the fill should occur on the paper API
    schedule: datetime | None = None
    #: delay before the fill happens on the paper API
    delay: timedelta | int | None = None

    @model_serializer(mode="wrap", when_used="json")
    def _split_sign_into_effect(
        self, handler: SerializerFunctionWrapHandler
    ) -> dict[str, Any]:
        data: dict[str, Any] = handler(self)
        for field in ["price", "value"]:
            effect = get_sign(getattr(self, field, None))
            if effect is not None:
                data[f"{field}-effect"] = effect.value
                data[field] = abs(getattr(self, field))
        return data


@deprecated(
    "`NewOrder` is deprecated and may be removed in the future. Use new order type "
    "classes like `LimitOrder` or `MarketOrder` instead."
)
class NewOrder(BaseOrder):
    """
    Dataclass containing information about a new order. Also used for
    modifying existing orders.
    """

    order_type: OrderType
    #: For a stop/stop limit order. If the latter, use price for the limit price
    stop_trigger: Decimal | None = None
    #: The price of the order; negative = debit, positive = credit
    price: Decimal | None = None
    #: The actual notional value of the order. Only for notional market orders!
    value: Decimal | None = None


class LimitOrder(BaseOrder):
    """
    A helper for defining limit orders to send to the API.
    """

    order_type: Literal[OrderType.LIMIT] = OrderType.LIMIT
    #: The price of the order; negative = debit, positive = credit
    price: Decimal


class MarketOrder(BaseOrder):
    """
    A helper for defining market orders to send to the API.
    """

    order_type: Literal[OrderType.MARKET] = OrderType.MARKET


class StopOrder(BaseOrder):
    """
    A helper for defining stop loss orders to send to the API.
    """

    order_type: Literal[OrderType.STOP] = OrderType.STOP
    #: Trigger price for the stop order to kick in
    stop_trigger: Decimal


class StopLimitOrder(BaseOrder):
    """
    A helper for defining stop limit orders to send to the API.
    """

    order_type: Literal[OrderType.STOP_LIMIT] = OrderType.STOP_LIMIT
    #: The price of the order; negative = debit, positive = credit
    price: Decimal
    #: Trigger price for the stop limit order to be placed
    stop_trigger: Decimal


class NotionalOrder(BaseOrder):
    """
    A helper for defining notional market orders to send to the API.
    """

    order_type: Literal[OrderType.NOTIONAL_MARKET] = OrderType.NOTIONAL_MARKET
    #: The actual notional value of the order. Only for notional market orders!
    value: Decimal


class BaseComplexOrder(TastytradeData):
    """
    Base class for different kinds of complex orders. For internal use.
    """

    source: str = version_str


@deprecated(
    "`NewComplexOrder` is deprecated and may be removed in the future. Use new order "
    "type classes like `OCOOrder` or `OTOCOOrder` instead."
)
class NewComplexOrder(BaseComplexOrder):
    """
    Dataclass containing information about a new OTOCO order.
    """

    orders: list[NewOrder]
    trigger_order: NewOrder | None = None
    type: ComplexOrderType = ComplexOrderType.OCO

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        if self.trigger_order is not None and self.type == ComplexOrderType.OCO:
            self.type = ComplexOrderType.OTOCO


AnyOrder = LimitOrder | StopOrder | StopLimitOrder | MarketOrder | NotionalOrder


class OCOOrder(BaseComplexOrder):
    """
    A helper for defining complex OCO orders to send to the API.
    """

    type: Literal[ComplexOrderType.OCO] = ComplexOrderType.OCO
    #: a limit order for taking profit versus the opening trade
    take_profit: LimitOrder = Field(exclude=True)
    #: a limit order for cutting off losses versus the opening trade
    stop_loss: StopOrder | StopLimitOrder = Field(exclude=True)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def orders(self) -> list[AnyOrder]:
        return [self.take_profit, self.stop_loss]


class OTOOrder(BaseComplexOrder):
    """
    A helper for defining complex OTO orders to send to the API.
    """

    type: Literal[ComplexOrderType.OTO] = ComplexOrderType.OTO
    #: an order that triggers one or more other orders upon fill
    trigger_order: AnyOrder
    #: orders to be triggered by the trigger order
    orders: list[AnyOrder] = Field(min_length=1, max_length=3)


class OTOCOOrder(BaseComplexOrder):
    """
    A helper for defining complex OTOCO orders to send to the API.
    """

    type: Literal[ComplexOrderType.OTOCO] = ComplexOrderType.OTOCO
    #: an order that triggers the take profit/stop loss orders upon fill
    trigger_order: AnyOrder
    #: a limit order for taking profit versus the opening trade
    take_profit: LimitOrder = Field(exclude=True)
    #: a limit order for cutting off losses versus the opening trade
    stop_loss: StopOrder | StopLimitOrder = Field(exclude=True)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def orders(self) -> list[AnyOrder]:
        return [self.take_profit, self.stop_loss]


class UnplacedOrder(TastytradeData):
    """
    Dataclass containing information about a test (dry run) order.
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
    size: Decimal | None = None
    price: Decimal | None = None
    gtc_date: date | None = None
    value: Decimal | None = None
    stop_trigger: Decimal | None = None
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


class PlacedOrder(UnplacedOrder):
    """
    Dataclass containing information about a live order, whether it's
    been filled or not.
    """

    #: the ID of the order
    id: int

    def average_fill_price(self) -> Decimal:
        total_price = Decimal(0)
        for leg in self.legs:
            if not leg.fills:
                raise TastytradeError("Can't calculate fill price without fills!")
            for fill in leg.fills:
                total_price += leg.action.multiplier * fill.fill_price * fill.quantity
        size = self.size or math.gcd(*[int(leg.quantity or 0) for leg in self.legs])
        return total_price / size


class PlacedLimitOrder(PlacedOrder):
    price: Decimal  # pyright: ignore


class PlacedStopOrder(PlacedOrder):
    stop_trigger: Decimal  # pyright: ignore


class PlacedStopLimitOrder(PlacedOrder):
    price: Decimal  # pyright: ignore
    stop_trigger: Decimal  # pyright: ignore


class PlacedNotionalOrder(PlacedOrder):
    value: Decimal  # pyright: ignore


T = TypeVar("T", bound=UnplacedOrder)
PLACED_TYPES: dict[OrderType, type[PlacedOrder]] = {
    OrderType.LIMIT: PlacedLimitOrder,
    OrderType.NOTIONAL_MARKET: PlacedNotionalOrder,
    OrderType.STOP: PlacedStopOrder,
    OrderType.STOP_LIMIT: PlacedStopLimitOrder,
}


class UnplacedComplexOrder(TastytradeData):
    """
    Dataclass containing information about a test (dry run) complex order.
    """

    account_number: str
    type: ComplexOrderType
    orders: list[UnplacedOrder]
    trigger_order: UnplacedOrder | None = None
    terminal_at: str | None = None
    ratio_price_threshold: Decimal | None = None
    ratio_price_comparator: str | None = None
    ratio_price_is_threshold_based_on_notional: bool | None = None
    related_orders: list[dict[str, str]] | None = None


class PlacedComplexOrder(UnplacedComplexOrder):
    """
    Dataclass containing information about an already placed complex order.
    """

    #: the ID of the complex order
    id: int


class PlacedOTOOrder(PlacedComplexOrder):
    trigger_order: PlacedOrder  # pyright: ignore


class PlacedOCOOrder(PlacedComplexOrder):
    @cached_property
    def take_profit(self) -> PlacedLimitOrder:
        return next(o for o in self.orders if o.order_type == OrderType.LIMIT)  # type: ignore

    @cached_property
    def stop_loss(self) -> PlacedStopOrder | PlacedStopLimitOrder:
        return next(o for o in self.orders if o.order_type != OrderType.LIMIT)  # type: ignore


class PlacedOTOCOOrder(PlacedOCOOrder):
    trigger_order: PlacedOrder  # pyright: ignore


C = TypeVar("C", bound=UnplacedComplexOrder)
PLACED_COMPLEX_TYPES: dict[type[BaseComplexOrder], type[PlacedComplexOrder]] = {
    OCOOrder: PlacedOCOOrder,
    OTOOrder: PlacedOTOOrder,
    OTOCOOrder: PlacedOTOCOOrder,
}


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


class PlacedComplexOrderResponse(TastytradeData, Generic[C]):
    """
    Dataclass grouping together information about a placed complex order.
    """

    buying_power_effect: BuyingPowerEffect
    complex_order: C
    fee_calculation: FeeCalculation | None = None
    warnings: list[Message] | None = None
    errors: list[Message] | None = None


class PlacedOrderResponse(TastytradeData, Generic[T]):
    """
    Dataclass grouping together information about a placed order.
    """

    buying_power_effect: BuyingPowerEffect
    order: T
    fee_calculation: FeeCalculation | None = None
    warnings: list[Message] | None = None
    errors: list[Message] | None = None
