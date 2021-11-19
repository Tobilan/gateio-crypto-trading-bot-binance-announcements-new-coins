import time
import unittest
from unittest.mock import patch
from SellClass.SellClass import *
from positionstorage.PositionStorage import PositionStorage
from logger import logger
import logging
import sys
logger = logging.getLogger()
logger.level = logging.DEBUG



class TestBuySellClass(unittest.TestCase):

    @patch('BuyClass.BuyClass.get_last_price')
    @patch('SellClass.SellClass.place_order')
    @patch('SellClass.SellClass.get_last_price')
    def test_buy_sell_cycle(self, get_last_price, place_order, buy_get_last_price):
        stream_handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(stream_handler)
        # set buy price to 30
        buy_get_last_price.return_value = 30
        logger.setLevel('DEBUG')
        logger.info('Testcase for buy sell cycle')
        globals.enable_tsl = True
        get_last_price.return_value = float(30)
        ps = PositionStorage('ETH')
        ps.start_trade()
        for price in range(30, 40, 1):
            # ramp up price of asset from 30 to 40
            get_last_price.return_value = float(price)
            place_order.assert_not_called()
            time.sleep(0.2)
        time.sleep(1)
        # price drop to 30
        get_last_price.return_value = 30
        time.sleep(1)
        # trailing stop loss should have executed the sell method exactly once during price drop
        place_order.assert_called_once()

