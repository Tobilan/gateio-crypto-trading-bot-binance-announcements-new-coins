import unittest

from unittest.mock import patch
from position import *

globals.enable_tsl = True
globals.tsl = -4
globals.ttp = 2
globals.tp = 2
globals.sl = -3
globals.test_mode = True


class TestPosition(unittest.TestCase):

    def test_instance(self):
        globals.enable_tsl = True
        position1 = Position('BTC', 80)
        assert position1.base == 'BTC'
        assert position1.initial_price == 80
        assert position1.tsl_percent == abs(globals.tsl) / 100
        assert position1.ttp_percent == abs(globals.ttp) / 100

    @patch('position.get_last_price')
    def test_update_price(self, get_last_price):
        globals.enable_tsl = True
        position3 = Position('ETH', 100)

        for price in range(101, 130, 1):
            get_last_price.return_value = float(price)
            position3.update()
            assert position3.current_price == float(price)

    @patch('position.place_order')
    @patch('position.get_last_price')
    def test_trailing_stop_loss(self, get_last_price, place_order):
        globals.enable_tsl = True
        position2 = Position('BTC', 80)
        for price2 in range(80, 100, 1):
            get_last_price.return_value = float(price2)
            position2.update()
            place_order.assert_not_called()

        assert position2.stop_loss == 77.6
        assert position2.trailing_stop_loss == 95.04

        get_last_price.return_value = 90
        position2.update()
        place_order.assert_called_once()

    @patch('position.place_order')
    @patch('position.get_last_price')
    def test_stop_loss_without_trailing(self, get_last_price, place_order):
        globals.enable_tsl = False
        globals.tp = 50
        position3 = Position('ETH', 100)
        assert position3.stop_loss == 97

        for price in range(100, 130, 1):
            get_last_price.return_value = float(price)
            position3.update()
            assert position3.stop_loss == 97
            place_order.assert_not_called()

        get_last_price.return_value = float(97.7)
        position3.update()
        place_order.assert_not_called()
        get_last_price.return_value = float(96.9)
        position3.update()
        place_order.assert_called_once()
        del position3
