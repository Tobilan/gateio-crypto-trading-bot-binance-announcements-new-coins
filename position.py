from trade_client import get_last_price, place_order
from logger import logger
import globals

return_price_only = True


class Position:

    def __init__(self, base, price):
        logger.info(f'Opened position: {base}, {price}')
        self.base = base
        self.quote = globals.pairing

        self.initial_price = price
        self.last_price = price
        self.current_price = price

        self.stop_loss = self.initial_price - (self.initial_price * abs(globals.sl) / 100)

        self.trailing_reference = price

        self.tsl_percent = abs(globals.tsl) / 100
        self.ttp_percent = abs(globals.ttp) / 100

        self.trailing_stop_loss = self.trailing_reference - (self.trailing_reference * self.tsl_percent)
        if (globals.enable_tsl):
            self.take_profit = self.initial_price + (self.initial_price * self.ttp_percent)
        else:
            self.take_profit = self.initial_price + (self.initial_price * globals.tp)



    def update_trailing(self):
        if self.current_price > self.trailing_reference:
            self.trailing_reference = self.current_price
            self.trailing_stop_loss = self.trailing_reference - (self.trailing_reference * self.tsl_percent)
            self.take_profit = self.trailing_reference + (self.trailing_reference * self.ttp_percent)
            logger.debug(f'update tsl to {self.trailing_stop_loss} and tp to {self.take_profit} ')

    def calc_trade_decision(self):
        if (self.current_price <= self.stop_loss) or (self.current_price <= self.trailing_stop_loss):
            logger.info(
                f'stop loss order at: {self.current_price} | stop_loss at: {self.stop_loss} | tsl at: {self.trailing_stop_loss}')
            amount = 10
            # TODO amount handling
            place_order(self.base, self.quote, amount, 'sell', self.current_price)
        elif (self.current_price > self.take_profit):
            logger.info(
                f'take profit order at: {self.current_price} | stop_loss at: {self.stop_loss} | tsl at: {self.trailing_stop_loss}')
            amount = 10
            # TODO amount handling
            place_order(self.base, self.quote, amount, 'sell', self.current_price)

    def update_price(self):
        self.current_price = get_last_price(self.base, self.quote, return_price_only)
        logger.debug(f'current price price for {self.base}: {self.current_price} in {self.quote}')

    def update(self):
        self.update_price()
        if (globals.enable_tsl):
            self.update_trailing()
        self.calc_trade_decision()
