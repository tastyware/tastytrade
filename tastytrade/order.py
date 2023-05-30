from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from tastytrade import VERSION
from tastytrade.utils import TastytradeJsonDataclass


class InstrumentType(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the valid types of instruments
    and their representation in the API.
    """
    BOND = 'Bond'
    CRYPTOCURRENCY = 'Cryptocurrency'
    CURRENCY_PAIR = 'Currency Pair'
    EQUITY = 'Equity'
    EQUITY_OFFERING = 'Equity Offering'
    EQUITY_OPTION = 'Equity Option'
    FUTURE = 'Future'
    FUTURE_OPTION = 'Future Option'
    INDEX = 'Index'
    UNKNOWN = 'Unknown'
    WARRANT = 'Warrant'


class OrderAction(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the valid order actions.
    """
    BUY_TO_OPEN = 'Buy to Open'
    BUY_TO_CLOSE = 'Buy to Close'
    SELL_TO_OPEN = 'Sell to Open'
    SELL_TO_CLOSE = 'Sell to Close'
    #: for futures only
    BUY = 'Buy'
    #: for futures only
    SELL = 'Sell'


class OrderStatus(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains different order statuses.
    A typical (successful) order follows a progression:

    RECEIVED -> LIVE -> FILLED
    """
    RECEIVED = 'Received'
    CANCELLED = 'Cancelled'
    FILLED = 'Filled'
    EXPIRED = 'Expired'
    LIVE = 'Live'
    REJECTED = 'Rejected'
    CONTINGENT = 'Contingent'
    ROUTED = 'Routed'
    IN_FLIGHT = 'In Flight'
    CANCEL_REQUESTED = 'Cancel Requested'
    REPLACE_REQUESTED = 'Replace Requested'
    REMOVED = 'Removed'
    PARTIALLY_REMOVED = 'Partially Removed'


class OrderTimeInForce(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the valid TIFs for orders.
    """
    DAY = 'Day'
    GTC = 'GTC'
    GTD = 'GTD'
    EXT = 'Ext'
    GTC_EXT = 'GTC Ext'
    IOC = 'IOC'


class OrderType(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the valid types of orders.
    """
    LIMIT = 'Limit'
    MARKET = 'Market'
    MARKETABLE_LIMIT = 'Marketable Limit'
    STOP = 'Stop'
    STOP_LIMIT = 'Stop Limit'
    NOTIONAL_MARKET = 'Notional Market'


class PriceEffect(str, Enum):
    """
    This is an :class:`~enum.Enum` that shows the sign of a price effect, since
    Tastytrade is apparently against negative numbers.
    """
    CREDIT = 'Credit'
    DEBIT = 'Debit'
    NONE = 'None'


class FillInfo(TastytradeJsonDataclass):
    """
    Dataclass that contains information about an order fill.
    """
    ext_group_fill_id: str
    ext_exec_id: str
    fill_id: str
    quantity: Decimal
    fill_price: Decimal
    filled_at: datetime
    destination_venue: str


class Leg(TastytradeJsonDataclass):
    """
    Dataclass that represents an order leg.

    Classes that inherit from :class:`TradeableTastytradeJsonDataclass` can
    call :meth:`build_leg` to build a leg from the dataclass.
    """
    instrument_type: InstrumentType
    symbol: str
    action: OrderAction
    quantity: Decimal
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
            action=action
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
        return f'{self.code}: {self.message}'


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
    source: str = f'tastyware/tastytrade:v{VERSION}'
    legs: list[Leg]
    gtc_date: Optional[date] = None
    stop_trigger: Optional[Decimal] = None
    price: Optional[Decimal] = None  # optional for market orders
    price_effect: Optional[PriceEffect] = None
    value: Optional[Decimal] = None
    value_effect: Optional[PriceEffect] = None
    partition_key: Optional[str] = None
    preflight_id: Optional[str] = None
    rules: Optional[OrderRule] = None


class PlacedOrder(TastytradeJsonDataclass):
    """
    Dataclass containing information about an existing order, whether it's
    been filled or not.
    """
    account_number: str
    time_in_force: OrderTimeInForce
    order_type: OrderType
    size: str
    underlying_symbol: str
    underlying_instrument_type: InstrumentType
    status: OrderStatus
    cancellable: bool
    editable: bool
    edited: bool
    updated_at: datetime
    legs: list[Leg]
    id: Optional[str] = None
    price: Optional[Decimal] = None
    price_effect: Optional[PriceEffect] = None
    gtc_date: Optional[date] = None
    value: Optional[Decimal] = None
    value_effect: Optional[PriceEffect] = None
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
    complex_order_id: Optional[str] = None
    complex_order_tag: Optional[str] = None
    preflight_id: Optional[str] = None
    order_rule: Optional[OrderRule] = None


class ComplexOrder(TastytradeJsonDataclass):
    """
    Dataclass containing information about a complex order.
    """
    id: str
    account_number: str
    type: str
    terminal_at: str
    ratio_price_threshold: Decimal
    ratio_price_comparator: str
    ratio_price_is_threshold_based_on_notional: bool
    related_orders: list[dict[str, str]]
    orders: list[PlacedOrder]
    trigger_order: PlacedOrder


class BuyingPowerEffect(TastytradeJsonDataclass):
    """
    Dataclass containing information about the effect of a trade on buying
    power.
    """
    change_in_margin_requirement: Decimal
    change_in_margin_requirement_effect: PriceEffect
    change_in_buying_power: Decimal
    change_in_buying_power_effect: PriceEffect
    current_buying_power: Decimal
    current_buying_power_effect: PriceEffect
    new_buying_power: Decimal
    new_buying_power_effect: PriceEffect
    isolated_order_margin_requirement: Decimal
    isolated_order_margin_requirement_effect: PriceEffect
    is_spread: bool
    impact: Decimal
    effect: PriceEffect


class FeeCalculation(TastytradeJsonDataclass):
    """
    Dataclass containing information about the fees associated with a trade.
    """
    regulatory_fees: Decimal
    regulatory_fees_effect: PriceEffect
    clearing_fees: Decimal
    clearing_fees_effect: PriceEffect
    commission: Decimal
    commission_effect: PriceEffect
    proprietary_index_option_fees: Decimal
    proprietary_index_option_fees_effect: PriceEffect
    total_fees: Decimal
    total_fees_effect: PriceEffect


class PlacedOrderResponse(TastytradeJsonDataclass):
    """
    Dataclass grouping together information about a placed order.
    """
    buying_power_effect: BuyingPowerEffect
    fee_calculation: FeeCalculation
    order: Optional[PlacedOrder] = None
    complex_order: Optional[ComplexOrder] = None
    warnings: Optional[list[Message]] = None
    errors: Optional[list[Message]] = None
