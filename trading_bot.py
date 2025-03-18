# Copyright 2019-2025, Orchard Forex
# https://orchardforex.com

import importlib
import modules.CustomMetatrader as mt5
import modules.util as util

# from backtesting import Backtest, Strategy
from classes.custom_backtesting import CustomBacktest, CustomStrategy

def main():

    # first load in the configuration
    config = util.load_config_from_args()
    config.params.timeframe = mt5.timeframe_value(config.params.timeframe)
    config.params.testing = config.testing # simple copy for the strategy

    # at this stage I'm going to trust you to set the config file correctly

    # now import the strategy named in the config
    strategy_file = 'strategy.' + config.strategy.file
    strategy_name = config.strategy.name
    strategy_module = importlib.import_module(strategy_file)
    strategy_class = getattr(strategy_module, strategy_name)

    # get mt5 ready, could be done elsewhere
    if not mt5.initialize(path=config.mt_path, portable=True):
        util.log("terminal initialisation failed")
        return
    util.log("MT5 successfully initialised")

    # get history data from mt, only using one instrument / tf for now
    # could get history both ways but just saving a little resource
    if config.testing:
        history = mt5.get_rates_frame(config.params.symbol, config.params.timeframe, 0, config.history_count)
    else:
        history = None

    # add custom arguments testing, cycle
    runner = CustomBacktest(history, strategy_class, testing=config.testing, cycle=config.cycle, cash=10000, hedging=True, finalize_trades=True)

    # add custom arguments testing, symbol, timeframe, magic
    result = runner.run(config=config.params)

    if config.testing:
        print(result)
    
    mt5.shutdown()
    return


if __name__ == "__main__":
    main()

# if you want the patched pandas_ta, at your own risk
# pip install -U git+https://github.com/OrchardForexTutorials/pandas-ta.git --no-cache-dir
