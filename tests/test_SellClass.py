import unittest
from unittest.mock import patch
from SellClass.SellClass import *
from positionstorage.PositionStorage import PositionStorage

globals.enable_tsl = True
globals.tsl = -4
globals.ttp = 2
globals.tp = 2
globals.sl = -3
globals.test_mode = True


"""
Unit-tests for class SellClass.
checks basic stuff:
    - working constructor
    - check update price method
    - check trailing stop loss method with an ease ramp up of the asset price with a fast drop in the end
    - check normal stop loss without trailing
"""

class TestSellClass(unittest.TestCase):

    def test_instance(self):
        globals.enable_tsl = True
        ps = PositionStorage('ETH')
        sellObj = SellClass(ps)
        assert sellObj.base == 'ETH'
        assert sellObj.tsl_percent == abs(globals.tsl) / 100
        assert sellObj.ttp_percent == abs(globals.ttp) / 100
        del sellObj
        del ps

    # mock get_last_price function to update price during test without API information
    @patch('SellClass.SellClass.get_last_price')
    def test_update_price(self, get_last_price):
        globals.enable_tsl = True
        ps = PositionStorage('ETH')
        sellObj = SellClass(ps)

        for price in range(101, 130, 1):
            get_last_price.return_value = float(price)
            sellObj.update()
            assert sellObj.current_price == float(price)
        del sellObj
        del ps

    # mock get_last_price function to update price during test without API information
    # mock the place_order to know, if it gets called
    @patch('SellClass.SellClass.place_order')
    @patch('SellClass.SellClass.get_last_price')
    def test_trailing_stop_loss(self, get_last_price, place_order):
        globals.enable_tsl = True
        ps = PositionStorage('ETH')
        ps.update_data(10, 80)
        sellObj = SellClass(ps)
        for price2 in range(80, 100, 1):
            get_last_price.return_value = float(price2)
            sellObj.update()
            place_order.assert_not_called()

        assert sellObj.stop_loss == 77.6
        assert sellObj.trailing_stop_loss == 95.04

        get_last_price.return_value = 90
        sellObj.update()
        place_order.assert_called_once()
        del sellObj
        del ps

    # mock get_last_price function to update price during test without API information
    # mock the place_order to know, if it gets called
    @patch('SellClass.SellClass.place_order')
    @patch('SellClass.SellClass.get_last_price')
    def test_stop_loss_without_trailing(self, get_last_price, place_order):
        globals.enable_tsl = False
        globals.tp = 50
        ps = PositionStorage('ETH')
        ps.update_data(10, 100)
        sellObj = SellClass(ps)
        assert sellObj.stop_loss == 97

        for price in range(100, 130, 1):
            get_last_price.return_value = float(price)
            sellObj.update()
            assert sellObj.stop_loss == 97
            place_order.assert_not_called()

        get_last_price.return_value = float(97.7)
        sellObj.update()
        place_order.assert_not_called()
        get_last_price.return_value = float(96.9)
        sellObj.update()
        place_order.assert_called_once()
        del sellObj
        del ps