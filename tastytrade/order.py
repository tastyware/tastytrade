from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

import aiohttp

from tastytrade import API_URL


class OrderType(Enum):
    LIMIT = "Limit"
    MARKET = "Market"


class OrderPriceEffect(Enum):
    CREDIT = "Credit"
    DEBIT = "Debit"


class OrderStatus(Enum):
    RECEIVED = "Received"
    CANCELLED = "Cancelled"
    FILLED = "Filled"
    EXPIRED = "Expired"
    LIVE = "Live"
    REJECTED = "Rejected"

    def is_active(self):
        return self in (OrderStatus.LIVE, OrderStatus.RECEIVED)


class TimeInForce(Enum):
    DAY = "Day"
    GTC = "GTC"
    GTD = "GTD"


@dataclass
class OrderDetails(object):
    type: OrderType
    time_in_force: TimeInForce = TimeInForce.DAY
    gtc_date: datetime = datetime.now()
    price: Optional[Decimal] = None
    price_effect: OrderPriceEffect = OrderPriceEffect.CREDIT
    status: Optional[OrderStatus] = None
    legs: List[str] = field(default_factory=list)
    source: str = "WBT"

    def is_executable(self) -> bool:
        required_data = all(
            [
                self.time_in_force,
                self.price_effect,
                self.price is not None,
                self.type,
                self.source,
            ]
        )

        if not required_data:
            return False

        if not self.legs:
            return False

        if self.time_in_force == TimeInForce.GTD:
            try:
                datetime.strptime(str(self.gtc_date), "%Y-%m-%d")
            except ValueError:
                return False

        return True


class Order:
    def __init__(self, order_details: OrderDetails):
        """
        Initiates a new order object.

        Args:
            order_details (OrderDetails): An object specifying order-level
            details.
        """
        self.details = order_details

    def check_is_order_executable(self):
        return self.details.is_executable()

    def add_leg(self, security: str):
        self.details.legs.append(security)

    @classmethod
    def from_dict(cls, input_dict: dict):
        """
        Parses an Order object from a dict.
        """
        details = OrderDetails(input_dict["underlying-symbol"])
        details.price = Decimal(input_dict["price"]) if "price" in input_dict else None
        details.price_effect = OrderPriceEffect(input_dict["price-effect"])
        details.type = OrderType(input_dict["order-type"])
        details.status = OrderStatus(input_dict["status"])
        details.time_in_force = input_dict["time-in-force"]
        details.gtc_date = input_dict.get("gtc-date", None)
        return cls(order_details=details)

    @classmethod
    async def get_remote_orders(cls, session, account, **kwargs) -> List:
        """
        Gets all orders on Tastyworks.

        Args:
            session (TastyAPISession): The session to use.
            account (TradingAccount): The account_id to get orders on.
            Keyword arguments specifying filtering conditions, these include:
            `status`, `time-in-force`, etc.

        Returns:
            list(Order): A list of Orders
        """
        if not session.logged_in:
            raise Exception("Tastyworks session not logged in.")

        filters = kwargs
        url = "{}/accounts/{}/orders".format(session.API_url, account.account_number)
        url = "{}?{}".format(url, "&".join([f"{k}={v}" for k, v in filters.items()]))

        res = []
        async with aiohttp.request(
            "GET", url, headers=session.get_request_headers()
        ) as resp:
            if resp.status != 200:
                raise Exception("Could not get current open orders")
            data = (await resp.json())["data"]["items"]
            for order_data in data:
                order = cls.from_dict(order_data)
                if not order.details.status.is_active():
                    continue
                res.append(order)
        return res

    async def execute_order(self, session, dry_run=True):
        """
        Execute an order. If doing a dry run, the order isn't placed but simulated (server-side).

        Args:
            session (TastyAPISession): The tastyworks session onto which to execute the order.
            dry_run (bool): Whether to do a test (dry) run.

        Returns:
            bool: Whether the order was successful.
        """
        if not self.check_is_order_executable():
            raise Exception("Order is not executable, most likely due to missing data")

        if not session.is_valid():
            raise Exception("The supplied session is not active and valid")

        url = f"{API_URL}/accounts/{self.account_number}/orders"
        if dry_run:
            url = f"{url}/dry-run"

        body = _get_execute_order_json(self)

        async with aiohttp.request(
            "POST", url, headers=session.get_request_headers(), json=body
        ) as resp:
            if resp.status == 201:
                return (await resp.json())["data"]
            elif resp.status == 400:
                raise Exception("Order execution failed: {}".format(await resp.text()))
            else:
                raise Exception(
                    "Unknown remote error {}: {}".format(resp.status, await resp.text())
                )


def _get_execute_order_json(order: Order):
    order_json = {
        "source": order.details.source,
        "order-type": order.details.type.value,
        "price": f"{order.details.price:.2f}",
        "price-effect": order.details.price_effect.value,
        "time-in-force": order.details.time_in_force.value,
        "legs": _get_legs_request_data(order),
    }

    if order.details.gtc_date:
        order_json["gtc-date"] = order.details.gtc_date.strftime("%Y-%m-%d")

    return order_json


def _get_legs_request_data(order):
    res = []
    order_effect = order.details.price_effect
    order_effect_str = (
        "Sell to Open" if order_effect == OrderPriceEffect.CREDIT else "Buy to Open"
    )
    for leg in order.details.legs:
        leg_dict = {**leg.to_tasty_json(), "action": order_effect_str}
        res.append(leg_dict)

    return res
