from threading import Thread
import threading
import time
from multiprocessing.pool import ThreadPool
from pycrunch_trace.client.api import trace


class Data:
    def __init__(self, name):
        self.name = name
        self.amount = 0
        self.investment = 0
        self.price_per_share = 0
        self.lock = threading.Lock()

    def get_data(self):
        with self.lock:
            return dict([self.amount, self.investment])

    def get_amount(self):
        with self.lock:
            return self.amount

    def update_data(self, amount, price):
        with self.lock:
            self.price_per_share = ((self.amount * self.price_per_share) + (amount * price)) / (self.amount + amount)
            self.investment += price
            self.amount += amount

    def sell_data(self, amount):
        with self.lock:
            self.amount -= amount

    def start_trade(self):
        buyThread = BuyClass(self)
        sellThread = SellClass(self)

        buyThread.start()
        sellThread.start()

class SellClass(Thread):
    def __init__(self, data):
        super(SellClass, self).__init__()
        self._stop_event = threading.Event()
        self.data = data
        self.sell = False
        self.proceed = True

    def stop(self):
        self._stop_event.set()

    def join(self, *args, **kwargs):
        self.stop()
        super(SellClass,self).join(*args, **kwargs)

    def output(self):
        if (self.data.get_amount() > 0):
            self.data.sell_position(1)
        print(f'after sell: {self.data.get_amount()}')

    def run(self):
        while not self._stop_event.isSet():
            if (self.data.get_amount() > 0):
                self.sell = True
            self.output()
            if (self.data.get_amount() <= 0) and self.sell:
                self.stop()
            time.sleep(0.1)


class BuyClass(Thread):
    def __init__(self, data):
        super(BuyClass, self).__init__()
        self._stop_event = threading.Event()
        self.data = data

    def stop(self):
        self._stop_event.set()

    def join(self, *args, **kwargs):
        self.stop()
        super(BuyClass,self).join(*args, **kwargs)

    def input_new_positions(self, amount, price):
        data.update_data(amount, price)
        print(f'after buy: {self.data.get_amount()}')

    def run(self):
        while not self._stop_event.isSet():
            for self.i in range(0, 3):
                self.input_new_positions(10, 30)
                time.sleep(0.6)
            self.stop()


if __name__ == "__main__":
    # data = Data('BTC',0,0)
    data = Data('BTC')

    data.start_trade()

    # buy1 = BuyClass(data)
    # buy2 = BuyClass(data)
    # buy3 = BuyClass(data)
    # buy4 = BuyClass(data)
    # buy5 = BuyClass(data)
    #
    # sell = SellClass(data)
    #
    # buy1.start()
    # sell.start()
    # buy2.start()
    # buy3.start()
    # buy4.start()
    # buy5.start()

