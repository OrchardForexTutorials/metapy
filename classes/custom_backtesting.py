# from abc import abstractmethod

from datetime import datetime
import pandas as pd
import time
from typing import Optional, Tuple, Type, Union

from backtesting import Backtest, Strategy
from backtesting._util import _Data

import modules.custom_metatrader as mt5

class CustomBacktest(Backtest):

    def __init__(self,
                 data: pd.DataFrame,
                 strategy: Type[Strategy],
                 *,
                 config = None,
                 cash: float = 10_000,
                 spread: float = .0,
                 commission: Union[float, Tuple[float, float]] = .0,
                 margin: float = 1.,
                 trade_on_close=False,
                 hedging=False,
                 exclusive_orders=False,
                 finalize_trades=False,
                 ):

        self.cycle = 10
        self.testing = True
        if config:
            for name in ["cycle", "testing"]:
                if hasattr(config, name): setattr(self, name, getattr(config, name))

        # create a blank data set
        if data is None:
            columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
            values = {col: [0] for col in columns}
            values['Time'] = [datetime.now()]
            data = pd.DataFrame(values)
            data.set_index('Time', inplace=True)

        # if data is None:
        #     # Define the number of rows
        #     num_rows = 50

        #     # Generate the DataFrame in a concise way
        #     data = pd.DataFrame({
        #         'Time': [datetime.now()] * num_rows,
        #         'Open': [0] * num_rows,
        #         'High': [0] * num_rows,
        #         'Low': [0] * num_rows,
        #         'Close': [0] * num_rows,
        #         'Volume': [0] * num_rows
        #     }).set_index('Time')  # Set 'Time' as the index
            
        super().__init__(data, strategy,
                         cash=cash, 
                         spread=spread, 
                         commission=commission, 
                         margin=margin, 
                         trade_on_close=trade_on_close, 
                         hedging=hedging, 
                         exclusive_orders=exclusive_orders, 
                         finalize_trades=finalize_trades)

    def run(self, **kwargs) -> pd.Series:

        if self.testing:
            return super().run(**kwargs)
        
        strategy: CustomStrategy = self._strategy(None, self._data, kwargs)

        if not mt5.symbol_select(strategy.config.symbol):
             return None
        
        strategy.init()

        # a loop just for testing
        while True:
            strategy.recalculate_indicators()
            strategy.next()
            time.sleep(self.cycle)

        return None

class CustomStrategy(Strategy):

    def __init__(self, broker, data, params):

        self.config = None
        self.is_calculated = False

        super().__init__(broker, data, params)

    def buy(self, *,
            size: float = 1.0,
            limit: Optional[float] = None,
            stop: Optional[float] = None,
            sl: Optional[float] = None,
            tp: Optional[float] = None,
            tag: object = None) -> 'Order':

        if self.config.testing:
            return super().buy(size=size, limit=limit, stop=stop, sl=sl, tp=tp, tag=tag)
                
        if sl is None:
            sl = 0.0
        if tp is None:
            tp = 0.0

        return mt5.open_position(mt5.ORDER_TYPE_BUY, self.symbol, size, sl=sl, tp=tp, magic=self.magic)

    def sell(self, *,
             size: float = 1.0,
             limit: Optional[float] = None,
             stop: Optional[float] = None,
             sl: Optional[float] = None,
             tp: Optional[float] = None,
             tag: object = None) -> 'Order':

        if self.config.testing:
            return super().sell(size=size, limit=limit, stop=stop, sl=sl, tp=tp, tag=tag)

        if sl is None:
            sl = 0.0
        if tp is None:
            tp = 0.0
            
        return mt5.open_position(mt5.ORDER_TYPE_SELL, self.symbol, size, sl=sl, tp=tp, magic=self.magic)

    # common functions that will take different paths on test

    # current prices
    def get_ask(self):
    
        if self.config.testing:
            return self.data.Close
        
        tick = mt5.get_tick_info(self.config.symbol)
        return tick.ask

    def get_bid(self):
    
        if self.config.testing:
            return self.data.Close
        
        tick = mt5.get_tick_info(self.config.symbol)
        return tick.bid

    def get_entry_price(self, type, *, sl_dist=0.0, tp_dist=0.0):
        if type==mt5.ORDER_TYPE_BUY:
            mult=1
            price = self.get_ask()
        elif type==mt5.ORDER_TYPE_SELL:
            mult=-1
            price = self.get_bid()
        else:
            return 0.0, 0.0, 0.0
        
        sl = price - (sl_dist * mult) if sl_dist>0.0 else 0.0
        tp = price + (tp_dist * mult) if tp_dist>0.0 else 0.0

        return price, sl, tp

    def get_position_count(self, type):

        open_trades = 0

        if self.config.testing:
            if type==mt5.ORDER_TYPE_BUY:
                open_trades = sum(1 for trade in self.trades if trade.is_long)
            elif type==mt5.ORDER_TYPE_SELL:
                open_trades = sum(1 for trade in self.trades if trade.is_long)
            return open_trades
        
        return mt5.get_position_count(symbol=self.symbol, type=type)
    
    def recalculate_indicators(self):
        if self.config.testing and self.is_calculated:
            return

        if not self.config.testing:
            data = mt5.get_rates_frame(self.config.symbol, self.config.timeframe, 0, self.depth)
            self._data = _Data(data.copy(deep=False))

        self.calculate_indicators()
        self.is_calculated = True
