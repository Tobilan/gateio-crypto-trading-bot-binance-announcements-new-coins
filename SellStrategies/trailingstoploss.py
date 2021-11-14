from trade_client import get_last_price, place_order
from logger import logger
import globals
import threading

# TODO this class needs updated data on the accumulated position during runtime. (thread-safe ! )
# TODO this means: amount to sell, mean-buy price of the position, the 'true' position ( minus fees)

return_price_only = True


class TrailingStopLoss(threading.Thread):
    """
    Handles selling of a position. Is able to sell according to trailing stop loss or only stop loss. Does this in a
    thread
    Args:
    'LTC', 300
    """

    def __init__(self, base, price):
        super().__init__()
        logger.info(f'Opened position: {base}, {price}')
        self.base = base
        self.quote = globals.pairing
        self.amount = 10
        self.initial_price = price
        self.last_price = price
        self.current_price = price

        self.stop_loss = self.initial_price - (self.initial_price * abs(globals.sl) / 100)

        self.trailing_reference = price

        self.tsl_percent = abs(globals.tsl) / 100
        self.ttp_percent = abs(globals.ttp) / 100

        self.trailing_stop_loss = self.trailing_reference - (self.trailing_reference * self.tsl_percent)
        if globals.enable_tsl:
            self.take_profit = self.initial_price + (self.initial_price * self.ttp_percent)
        else:
            self.take_profit = self.initial_price + (self.initial_price * globals.tp)

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
            place_order(self.base, self.quote, self.amount, 'sell', self.current_price)
        elif (self.current_price > self.take_profit):
            logger.info(
                f'take profit order at: {self.current_price} | stop_loss at: {self.stop_loss} | tsl at: {self.trailing_stop_loss}')
            place_order(self.base, self.quote, self.amount, 'sell', self.current_price)

    def update_price(self):
        self.current_price = float(get_last_price(self.base, self.quote, return_price_only))
        logger.debug(f'current price price for {self.base}: {self.current_price} in {self.quote}')

    def update(self):
        self.update_price()
        if (globals.enable_tsl):
            self.update_trailing()
        self.calc_trade_decision()

    def run(self):
        """
        inherited from threading
        """
        logger.info(f'start thread for selling position: {self.base}')
        while self.amount > 0:
            self.update()
            time.sleep(.01)

        logger.info(f'stop thread for selling position: {self.base}')


if __name__ == '__main__':
    """
    short example
    """
    import time

    logger.setLevel('DEBUG')
    globals.test_mode = True
    example = TrailingStopLoss('LTC', 265)
    example.start()
    time.sleep(5)
    example.amount = 0
