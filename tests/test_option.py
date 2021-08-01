import unittest
from datetime import date
from decimal import Decimal

from tastyworks.models.option import Option, OptionType
from tastyworks.models.underlying import UnderlyingType


class TestOptionModel(unittest.TestCase):
    def setUp(self):
        self.test_option = Option(
            ticker='AKS',
            quantity=1,
            expiry=date(2018, 8, 10),
            strike=Decimal('3.5'),
            option_type=OptionType.CALL,
            underlying_type=UnderlyingType.EQUITY
        )

    def test_occ2010_integer_strike(self):
        self.test_option.strike = 3
        expected_result = 'AKS   180810C00003000'

        res = self.test_option.get_occ2010_symbol()
        self.assertEqual(expected_result, res)

    def test_occ2010_fraction_strike(self):
        self.test_option.strike = 3.45
        expected_result = 'AKS   180810C00003450'

        res = self.test_option.get_occ2010_symbol()
        self.assertEqual(expected_result, res)

        self.test_option.strike = 3.5
        expected_result = 'AKS   180810C00003500'

        res = self.test_option.get_occ2010_symbol()
        self.assertEqual(expected_result, res)

    def test_occ2010_ticker_padding(self):
        self.test_option.ticker = 'BOB123'
        expected_result = 'BOB123180810C00003500'

        res = self.test_option.get_occ2010_symbol()
        self.assertEqual(expected_result, res)

        self.test_option.ticker = 'BOB'
        expected_result = 'BOB   180810C00003500'

        res = self.test_option.get_occ2010_symbol()
        self.assertEqual(expected_result, res)

    def test_occ2010_ticker_trimming(self):
        self.test_option.ticker = 'BOB123456'
        expected_result = 'BOB123180810C00003500'

        res = self.test_option.get_occ2010_symbol()
        self.assertEqual(expected_result, res)

    def test_get_dxfeed_symbol(self):
        expected_result = '.AKS180810C3.5'
        result = self.test_option.get_dxfeed_symbol()
        self.assertEqual(result, expected_result)

    def test_no_option_chains_on_option(self):
        with self.assertRaises(Exception):
            self.test_option.get_option_chain()

    def test_get_underlying_type_string(self):
        res = self.test_option._get_underlying_type_string(UnderlyingType.EQUITY)
        self.assertEqual(res, 'Equity Option')

    def test_to_tasty_json(self):
        res = self.test_option.to_tasty_json()
        expected_result = {
            'instrument-type': 'Equity Option',
            'symbol': 'AKS   180810C00003500',
            'quantity': 1
        }
        self.assertDictEqual(res, expected_result)
