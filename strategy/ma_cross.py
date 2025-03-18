
import modules.CustomMetatrader as mt5
import pandas as pd
import pandas_ta as ta # take care with this

from classes.custom_backtesting import CustomStrategy

class MACross(CustomStrategy):
    
    def init(self):

        self.fast_ma_period = 10
        self.slow_ma_period = 20
        self.depth = 40

        self.lot_size = 0.01
        self.stop_loss_amount = 0.00100
        self.take_profit_amount = 0.00150

        self.buy_count = 0
        self.sell_count = 0

        self.recalculate_indicators()

        pass

    def next(self):

        # Check for crossover
        # amended to trade on ma relative to make testing quicker
        # if self.fast_ma[-1] > self.slow_ma[-1] and self.fast_ma[-2] <= self.slow_ma[-2]:
        if self.fast_ma[-1] > self.slow_ma[-1]:

            # Fast MA crosses above Slow MA: Buy signal
            open_trades = self.get_position_count(mt5.ORDER_TYPE_BUY)
            if open_trades > 0:
                return

            stop_loss_price = self.data.Close[-1]-self.stop_loss_amount
            take_profit_price = self.data.Close[-1]+self.take_profit_amount
            self.buy(size = self.lot_size, sl = stop_loss_price, tp = take_profit_price)
            self.buy_count += 1

        # elif self.fast_ma[-1] < self.slow_ma[-1] and self.fast_ma[-2] >= self.slow_ma[-2]:
        elif self.fast_ma[-1] < self.slow_ma[-1]:

            # Slow MA crosses above Fast MA: Sell signal
            open_trades = self.get_position_count(mt5.ORDER_TYPE_SELL)
            if open_trades > 0:
                return

            stop_loss_price = self.data.Close[-1]+self.stop_loss_amount
            take_profit_price = self.data.Close[-1]-self.take_profit_amount
            self.sell(size = self.lot_size, sl = stop_loss_price, tp = take_profit_price)
            self.sell_count += 1



    def calculate_indicators(self):

        # Calculate fast and slow moving averages
        self._indicators.clear()
        self.fast_ma = self.I(SMA, self.data.Close, self.fast_ma_period)
        self.slow_ma = self.I(SMA, self.data.Close, self.slow_ma_period)

# Define Simple Moving Average (SMA) function
def SMA(data, period):
    return ta.sma(pd.Series(data), length = period).to_numpy()
