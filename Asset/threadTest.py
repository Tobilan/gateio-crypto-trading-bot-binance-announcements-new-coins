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


class SellClass(Thread):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.sell = False
        self.proceed = True

    def output(self):
        if (self.data.get_amount() > 0):
            self.data.sell_data(1)
        print(f'after sell: {self.data.get_amount()}')

    def run(self):
        while self.proceed:
            if (self.data.get_amount() > 0):
                self.sell = True
            self.output()
            if (self.data.get_amount() <= 0) and self.sell:
                self.proceed = False
            time.sleep(0.1)


class BuyClass(Thread):
    def __init__(self, data):
        super().__init__()
        self.data = data

    def input_new_positions(self, amount, price):
        data.update_data(amount, price)
        # print(f'updated with: {amount} {price}')
        print(f'after buy: {self.data.get_amount()}')

    def run(self):
        for i in range(0, 10):
            self.input_new_positions(10, 30)
            time.sleep(0.6)


if __name__ == "__main__":
    # data = Data('BTC',0,0)
    data = Data('BTC')

    buy1 = BuyClass(data)
    buy2 = BuyClass(data)
    buy3 = BuyClass(data)
    buy4 = BuyClass(data)
    buy5 = BuyClass(data)

    sell = SellClass(data)

    buy1.start()
    sell.start()
    # buy2.start()
    # buy3.start()
    # buy4.start()
    # buy5.start()

