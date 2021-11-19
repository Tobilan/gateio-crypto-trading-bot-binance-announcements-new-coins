from trade_client import get_last_price, place_order
from logger import logger
import globals
from threading import Thread,Event
import time


# TODO this class needs updated data on the accumulated position during runtime. (thread-safe ! )
# TODO this means: amount to sell, mean-buy price of the position, the 'true' position ( minus fees)

return_price_only = True


class SellClass(Thread):
    """
    Handles selling of a position. Is able to sell according to trailing stop loss or only stop loss. Does this in a
    thread
    """

    def __init__(self, positionStorage):
        super(SellClass,self).__init__()
        self._monitor_position = Event()
        self._monitor_position.set()
        self.positionStorage = positionStorage
        self.base = positionStorage.get_name()
        logger.info(f'Begin to monitor position: {self.base}')

        self.quote = globals.pairing
        self.tsl_percent = abs(globals.tsl) / 100
        self.ttp_percent = abs(globals.ttp) / 100

        self.amount = self.positionStorage.get_amount()
        self.base_price = self.positionStorage.get_average_price()
        self.last_price = self.positionStorage.get_average_price()
        self.current_price = self.positionStorage.get_average_price()
        self.trailing_reference = self.positionStorage.get_average_price()

        self.stop_loss = self.base_price - (self.base_price * abs(globals.sl) / 100)
        self.trailing_stop_loss = self.trailing_reference - (self.trailing_reference * self.tsl_percent)

        if globals.enable_tsl:
            self.take_profit = self.base_price + (self.base_price * self.ttp_percent)
        else:
            self.take_profit = self.base_price + (self.base_price * globals.tp)


    def update_trailing(self):
        """
        updates all trailing boundaries
        """
        if self.current_price > self.trailing_reference:
            self.trailing_reference = self.current_price
            self.trailing_stop_loss = self.trailing_reference - (self.trailing_reference * self.tsl_percent)
            self.take_profit = self.trailing_reference + (self.trailing_reference * self.ttp_percent)
            logger.debug(f'update tsl to {self.trailing_stop_loss} and tp to {self.take_profit} ')

    def calc_trade_decision(self):
        """
        decides, whether the position should get sold
        """
        if (self.current_price <= self.stop_loss) or (self.current_price <= self.trailing_stop_loss):
            logger.info(
                f'stop loss order at: {self.current_price} | stop_loss at: {self.stop_loss} | tsl at: {self.trailing_stop_loss}')
            self.sell()

        elif (self.current_price > self.take_profit):
            logger.info(
                f'take profit order at: {self.current_price} | stop_loss at: {self.stop_loss} | tsl at: {self.trailing_stop_loss}')
            self.sell()


    def sell(self):
        # TODO: Implement logic for partial sells and handling of return object 'order' of the place_order method
        place_order(self.base, self.quote, self.amount, 'sell', self.current_price)
        self.positionStorage.sell_position(self.amount)
        if self.positionStorage.get_amount() <= 0:
            self.stop()

    def update_price(self):
        self.current_price = float(get_last_price(self.base, self.quote, return_price_only))
        logger.info(f'current price price for {self.base}: {self.current_price} in {self.quote}')

    def update_position(self):
        self.amount = self.positionStorage.get_amount()
        self.base_price = self.positionStorage.get_average_price()
        logger.debug(f'updated position:  {self.amount}: {self.base_price} in {self.quote}')


    def stop(self):
        self._monitor_position.clear()

    def join(self, *args, **kwargs):
        self.stop()
        super(SellClass, self).join(*args, **kwargs)

    def update(self):
        self.update_position()
        self.update_price()
        if globals.enable_tsl:
            self.update_trailing()


        self.calc_trade_decision()

    def run(self):
        """
        inherited from threading
        """
        logger.info(f'start thread for selling position: {self.base}')
        while self._monitor_position.isSet():
            self.update()
            time.sleep(.01)

        logger.info(f'stop thread for selling position: {self.base}')



