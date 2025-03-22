
import modules.custom_metatrader as mt5
from modules.indicators import rsi

from classes.custom_backtesting import CustomStrategy
from pandas_ta import Series as Series

class RSITrend(CustomStrategy):
    
    def init(self):

        self.depth = self.config.period+3

        self.high_trigger_set = False
        self.low_trigger_set = False

        self.recalculate_indicators()

    def next(self):

        # just write the rules

        # set triggers if rsi has gone above high or below low limits
        value = self.rsi[-1]
        if value > self.config.high_trigger:
            self.high_trigger_set = True
            self.low_trigger_set = False

        elif value < self.config.low_trigger:
            self.low_trigger_set = True
            self.high_trigger_set = False

        # now if a trigger is set and rsi has moved past entry
        elif self.high_trigger_set and value < self.config.high_entry:

            price, sl, tp = self.get_entry_price(mt5.ORDER_TYPE_SELL, sl_dist=self.config.sl, tp_dist=self.config.tp)
            self.sell(size = self.config.volume, sl = sl, tp = tp)

            self.high_trigger_set = False
            self.low_trigger_set = False

        elif self.low_trigger_set and value > self.config.low_entry:

            price, sl, tp = self.get_entry_price(mt5.ORDER_TYPE_BUY, sl_dist=self.config.sl, tp_dist=self.config.tp)
            self.buy( size = self.config.volume, sl = sl, tp = tp)

            self.high_trigger_set = False
            self.low_trigger_set = False

    def calculate_indicators(self):

        self._indicators.clear()
        self.rsi = self.I(rsi, self.data.Close, self.config.period)

