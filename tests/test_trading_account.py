import datetime
import unittest
from decimal import Decimal

from tastyworks.models import option, order, trading_account, underlying

GTC_DATE = '2019-02-12'


def build_default_order(time_in_force=order.TimeInForce.DAY):
    order_details = order.OrderDetails(
        type=order.OrderType.LIMIT,
        price=Decimal(400),
        price_effect=order.OrderPriceEffect.CREDIT,
        time_in_force=time_in_force,
        gtc_date=datetime.datetime(2019, 2, 12) if time_in_force == order.TimeInForce.GTD else None
    )
    order_details.legs = [
        option.Option(
            ticker='AKS',
            expiry=datetime.date(2018, 8, 31),
            strike=Decimal('3.5'),
            option_type=option.OptionType.CALL,
            underlying_type=underlying.UnderlyingType.EQUITY,
            quantity=1
        )
    ]
    return order.Order(order_details)


class TestTradingAccount(unittest.TestCase):
    def test_get_execute_order_json(self):
        test_order = build_default_order()
        res = trading_account._get_execute_order_json(test_order)
        expected_result = {
            'source': 'WBT',
            'order-type': 'Limit',
            'price': '400.00',
            'price-effect': 'Credit',
            'time-in-force': 'Day',
            'legs': [
                {
                    'instrument-type': 'Equity Option',
                    'symbol': 'AKS   180831C00003500',
                    'quantity': 1,
                    'action': 'Sell to Open'
                }
            ]
        }

        self.assertDictEqual(res, expected_result)

    def test_get_execute_order_json_when_gtd(self):
        test_order = build_default_order(order.TimeInForce.GTD)
        res = trading_account._get_execute_order_json(test_order)
        expected_result = {
            'source': 'WBT',
            'order-type': 'Limit',
            'price': '400.00',
            'price-effect': 'Credit',
            'time-in-force': 'GTD',
            'gtc-date': GTC_DATE,
            'legs': [
                {
                    'instrument-type': 'Equity Option',
                    'symbol': 'AKS   180831C00003500',
                    'quantity': 1,
                    'action': 'Sell to Open'
                }
            ]
        }

        self.assertDictEqual(res, expected_result)
