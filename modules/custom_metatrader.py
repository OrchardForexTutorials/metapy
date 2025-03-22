from MetaTrader5 import *
import pandas as pd

# Automatically generate the mapping dictionary
_TIMEFRAME_MAPPING = {name.split('_')[1]: globals()[name] for name in dir() if name.startswith("TIMEFRAME_")}

# Open order
def open_position(type, symbol, volume=0.0, price=None, *, sl=0.0, tp=0.0, sl_points=0, tp_points=0, deviation=0, magic=0, comment=None, retries=10):

    if price is not None:

        request = _request(type, symbol, volume, price, sl=sl, tp=tp, sl_points=sl_points, tp_points=tp_points, deviation=deviation, magic=magic, comment=comment)
        if request is None:
            print("invalid order request")
            return None

        return order_send(request)

    # no price, we try several times with current price
    response = None
    for tries in range(retries):

        request = _request(type, symbol, volume, None, sl=sl, tp=tp, comment=comment)
        if request is None:
            continue

        response = order_send(request)
        if response is None:
            return None
        if response.retcode != TRADE_RETCODE_REQUOTE and response.retcode != TRADE_RETCODE_PRICE_OFF:
            return response

    return response
    

# information sets

def get_position_count(*, symbol=None, type = None, magic=None):

    if symbol is None:
        positions = positions_get()
    else:
        positions = positions_get(symbol=symbol)

    if positions is None:
        return 0

    positions = [position for position in positions
                    if (type is None or position.type == type) and
                        (magic is None or position.magic == magic)
                ]
    
    return len(positions)

def get_rates_frame(symbol, timeframe, start, count):

    rates = copy_rates_from_pos(symbol, timeframe, start, count)        
    if rates is None:
        print('No rates data retrieved')
        return None

    rates_frame = pd.DataFrame(rates)
    rates_frame.rename(columns={'time':'Time', 'open':'Open', 'high':'High', 'low':'Low', 'close':'Close', 'tick_volume':'Volume'}, inplace=True)
    rates_frame['Time'] = pd.to_datetime(rates_frame['Time'], unit='s')
    rates_frame.set_index('Time', inplace=True)

    return rates_frame

# Support
def _request(type, symbol, volume, price=None, *, sl=0.0, tp=0.0, sl_points=0, tp_points=0, deviation=10, magic=0, comment=None):

    if price is None:
        # current price information
        price_info = symbol_info_tick(symbol)
        if price_info is None:
            print(f"Failed to get price information for {symbol}")
            return None
        
        if type == ORDER_TYPE_BUY:
            trade_price = price_info.ask
        else: 
            trade_price = price_info.bid

    else:
        trade_price = price

    request = {
        "action":       TRADE_ACTION_DEAL,
        "symbol":       symbol,
        "volume":       volume,
        "type":         type,
        "price":        trade_price,
        "sl":           sl,
        "tp":           tp,
        "magic":        magic,
        "deviation":    deviation,
    }
    if comment is not None:
        request["comment"] = comment

    # if not _SetFillingMode(request):
    #     return None

    return request

# simple utilities
def timeframe_value(name):

    # Access a specific timeframe
    return(_TIMEFRAME_MAPPING.get(name))

def _SetFillingMode(request):

    for filling_mode in {ORDER_FILLING_FOK, ORDER_FILLING_IOC, ORDER_FILLING_RETURN, ORDER_FILLING_BOC}:
        request['type_filling'] = filling_mode
        result = order_check(request)
        if result.retcode == 0:
            return True
    
    return False
