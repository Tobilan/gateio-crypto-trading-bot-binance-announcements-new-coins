from trade_client import get_last_price, place_order
from threading import Thread,Event
import time
import globals
from logger import logger

return_price_only = True

class BuyClass(Thread):
    def __init__(self, positionStorage):
        super(BuyClass, self).__init__()
        self.base = positionStorage.get_name()
        self.quote = globals.pairing
        self._stop_buy_event = Event()
        self.positionStorage = positionStorage
        self.max_amount = self.positionStorage.get_max_amount()

    def stop(self):
        self._stop_buy_event.set()

    def join(self, *args, **kwargs):
        self.stop()
        super(BuyClass,self).join(*args, **kwargs)

    def input_new_positions(self, amount, price):


        current_price = float(get_last_price(self.base, self.quote, return_price_only))
        self.positionStorage.update_data(amount, current_price)

        # volume = 10
        #     TODO Buy order stuff
        # place_order(self.base, globals.pairing, volume, 'buy', current_price)

    def buy(self,amount):
        self.input_new_positions(amount, 30)

    def run(self):
        time.sleep(0.6)
        self.buy(15)
        # self.buy(self.positionStorage.max_amount)
        # while not self._stop_buy_event.isSet():
        #     self.buy(self.positionStorage.max_amount)
        #     # TODO buy order stuff
        #     time.sleep(0.6)
        # self.stop()


