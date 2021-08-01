import unittest

from tastyworks.models.order import OrderStatus


class TestOrderStatus(unittest.TestCase):
    def setUp(self):
        pass

    def test_is_active(self):
        new_status = OrderStatus.LIVE
        self.assertTrue(new_status.is_active())

        new_status = OrderStatus.RECEIVED
        self.assertTrue(new_status.is_active())

    def test_is_active_false(self):
        new_status = OrderStatus.CANCELLED
        self.assertFalse(new_status.is_active())

        new_status = OrderStatus.EXPIRED
        self.assertFalse(new_status.is_active())
