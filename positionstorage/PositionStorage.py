"""
TODO: central information of the opened position is stored here. Gets instantiated if a new announcement is detected.
   - starts buy-thread (maybe also a class)
   - handles accumulated position and stops buy-thread if the desired position is reached
   - with the first successful buy of a coin a Instance of TrailingStopLoss gets opened and executed in its own thread
   - if TrailingStopLoss-thread stops, the position is closed and the asset is not active anymore
   - -> logging, handling of accumulated positions when bot gets restarted (decorators, json export to local machine)

   The idea is, to construct this class with every detected listing (-> easy multi-listing support)
"""
import globals
from logger import logger
import threading
from BuyClass.BuyClass import BuyClass
from SellClass.SellClass import SellClass

class PositionStorage:
    def __init__(self, name):
        self.name = name
        self.amount = 0
        self.investment = 0
        self.average_price = 0
        self.lock = threading.Lock()
        self.max_amount = globals.quantity

        self.buyThread = BuyClass(self)
        self.sellThread = SellClass(self)


    def get_max_amount(self):
        with self.lock:
            return self.max_amount
            # return 15

    def get_amount(self):
        with self.lock:
            return self.amount

    def get_name(self):
        return self.name

    def get_average_price(self):
        with self.lock:
            return self.average_price

    def update_data(self, amount, price):
        with self.lock:
            self.average_price = ((self.amount * self.average_price) + (amount * price)) / (self.amount + amount)
            self.investment += price
            self.amount += amount
            logger.debug(f'Position update for: {self.name} , new amount: {self.amount}, average price: {self.average_price}')

    def sell_position(self, amount):
        with self.lock:
            self.amount -= amount
        self.buyThread.stop()


    def start_trade(self):
        self.buyThread.start()
        self.sellThread.start()

    def stop_trade(self):
        self.buyThread.stop()
        self.sellThread.stop()

if __name__ == "__main__":

    logger.setLevel('DEBUG')
    data = PositionStorage('ETH')
    data.start_trade()
