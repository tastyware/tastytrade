from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


class OrderType(str, Enum):
    LIMIT = 'Limit'
    MARKET = 'Market'


class PriceEffect(str, Enum):
    CREDIT = 'Credit'
    DEBIT = 'Debit'


class OrderStatus(str, Enum):
    RECEIVED = 'Received'
    CANCELLED = 'Cancelled'
    FILLED = 'Filled'
    EXPIRED = 'Expired'
    LIVE = 'Live'
    REJECTED = 'Rejected'

    def is_active(self):
        return self in (OrderStatus.LIVE, OrderStatus.RECEIVED)


class TimeInForce(str, Enum):
    DAY = 'Day'
    GTC = 'GTC'
    GTD = 'GTD'


@dataclass
class Order:
    id: str
    account_number: str
    time_in_force: TimeInForce
    gtc_date: date
    order_type: OrderType
    size: str
    underlying_symbol: str
    underlying_instrument_type: str
    price: Decimal
    price_effect: PriceEffect
    value: Decimal
    value_effect: PriceEffect
    stop_trigger: str
    status: OrderStatus
    contingent_status: str
    confirmation_status: str
    cancellable: bool
    cancelled_at: datetime
    cancel_user_id: str
    cancel_username: str
    editable: bool
    edited: bool
    replacing_order_id: str
    replaces_order_id: str
    received_at: datetime
    updated_at: datetime
    in_flight_at: datetime
    live_at: datetime
    reject_reason: str
    user_id: str
    username: str
    terminal_at: datetime
    complex_order_id: str
    complex_order_tag: str
    preflight_id: str
    legs: list
    order_rule: dict
