import unittest
from datetime import date
from decimal import Decimal

from tastyworks.models import option, option_chain, underlying


class TestOptionChain(unittest.TestCase):
    def setUp(self):
        options = [option.Option(
            ticker='AKS',
            expiry=date(2018, 1, 21),
            strike=Decimal('3.5'),
            option_type=option.OptionType.PUT,
            underlying_type=underlying.UnderlyingType.EQUITY
        ), option.Option(
            ticker='AKS',
            expiry=date(2018, 2, 21),
            strike=Decimal(4),
            option_type=option.OptionType.PUT,
            underlying_type=underlying.UnderlyingType.EQUITY
        )]

        self.option_chain = option_chain.OptionChain(options)

    def test_constructor(self):
        self.assertEqual(len(self.option_chain.options), 2)

    def test_get_all_strikes(self):
        expected_result = [3.5, 4]
        result = self.option_chain.get_all_strikes()
        self.assertListEqual(result, expected_result)

    def test_get_all_strikes_no_duplicates(self):
        self.option_chain.options.append(option.Option(
            ticker='AKS',
            expiry=date(2018, 4, 21),
            strike=Decimal('3.5'),
            option_type=option.OptionType.PUT,
            underlying_type=underlying.UnderlyingType.EQUITY
        ))
        expected_result = [3.5, 4]
        result = self.option_chain.get_all_strikes()
        self.assertListEqual(result, expected_result)

    def test_get_all_expirations(self):
        expected_result = [date(2018, 1, 21), date(2018, 2, 21)]
        result = self.option_chain.get_all_expirations()
        self.assertListEqual(result, expected_result)

    def test_get_all_expirations_no_duplicates(self):
        self.option_chain.options.append(option.Option(
            ticker='AKS',
            expiry=date(2018, 2, 21),
            strike=Decimal('3.5'),
            option_type=option.OptionType.PUT,
            underlying_type=underlying.UnderlyingType.EQUITY
        ))
        expected_result = [date(2018, 1, 21), date(2018, 2, 21)]
        result = self.option_chain.get_all_expirations()
        self.assertListEqual(result, expected_result)
