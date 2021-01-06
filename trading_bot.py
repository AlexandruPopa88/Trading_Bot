from datetime import datetime
import pytz

def initialize(state):
    #candles
    state.candles_1m = list()
    state.candles_1h = list()
    state.candles_4h = list()
    state.candles_1d = list()
    state.active_candle_1m = None
    state.start_candles = False
    state.start_buy = False
    
    #orders
    state.entry_price = None
    state.stop_price = None
    state.trailing_stop_price = 0
    state.trailing_unrealized_pnl = 0
    state.buy_amount = None
    state.has_position = False
    state.has_active_order = False
    state.balance_saved = 0

def cleanup_candles(inlist, days):
    temp = inlist[:]
    for i in range(len(inlist)):
        if (datetime.now(pytz.UTC) - inlist[i].candle_time).days > days:
            del(temp[i])
    return temp

class candle(object):
    def __init__(self, candle_time, opened, high, low, closed, volume, time_frame):
        self.candle_time = candle_time
        self.open = opened
        self.high = high
        self.low = low
        self.close = closed
        self.volume = volume
        self.time_frame = time_frame
        self.color = "unassigned"
        self.order = 0
        
    def __str__(self):
        return f'{self.candle_time.strftime("%d.%m.%y %H:%M")}, o: {self.open}, h: {self.high}, l: {self.low}, c: {self.close} , v: {self.volume}, t: {self.time_frame}, co: {self.color}, or: {self.order}'
    
    def __repr__(self):
        return self.candle_time.strftime("%d.%m.%y %H:%M")

def set_candle(last_candle, time_frame, data = None, inlist = None):
    if data:
        return candle(last_candle, data.open_last, data.high_last,
            data.low_last, data.close_last, data.volume_last, time_frame)
    elif inlist:
        return candle(last_candle, inlist[0].open, 
                                    max([i.high for i in inlist]),
                                    min([i.low for i in inlist]),
                                    inlist[-1].close,
                                    round(sum([i.volume for i in inlist]),2), time_frame)

def color_order(inlist):
    if inlist[-1].close > inlist[-5].close:
        inlist[-1].color = "green"
        if inlist[-2].color == "red":
            inlist[-1].order = 1
        else:
            inlist[-1].order = (inlist[-2].order + 1) % 9
            if inlist[-1].order == 0:
                inlist[-1].order = 9
    else:
        inlist[-1].color = "red"
        if inlist[-2].color == "green":
            inlist[-1].order = 1
        else:
            inlist[-1].order = (inlist[-2].order + 1) % 9
            if inlist[-1].order == 0:
                inlist[-1].order = 9

def set_buy_ammount(global_vars):
    return ((float(query_balance_free("USDT")) * 0.009985) / (global_vars.entry_price - global_vars.stop_price)) * global_vars.entry_price

def hour_passed(position, active_candle):
    buy_time = datetime.fromtimestamp(position.entry_time // 1000, pytz.UTC)
    buy_time = buy_time.replace(minute = 0)
    return (active_candle.candle_time - buy_time).seconds > 7200


@schedule(interval="1m", symbol="BTCUSDT", window_size = 1)
def minuter(state, data):
    try:
        last_candle = datetime.fromtimestamp(data.last_time // 1000, pytz.UTC)
    except:
        print("Last candle is None")
    else:
        if not state.start_candles and last_candle.minute != 1:
            if last_candle.minute == 0:
                state.start_candles = True
        else:
            if not state.start_candles:
                state.start_candles = True
            
            #candle algorithm
            state.candles_1m.append(set_candle(last_candle, "1m", data = data))
            state.active_candle_1m = state.candles_1m[-1]
            
            #setting up 1h candles and appending them to list
            if len(state.candles_1m) == 60:
                state.candles_1h.append(set_candle(last_candle, "1h", inlist = state.candles_1m))
                state.candles_1m = list()

                #setting up 4h candles and appending them to list
                if len(state.candles_1h) == 4:
                    state.candles_4h.append(set_candle(last_candle, "4h", inlist = state.candles_1h))
                    state.candles_1h = list()
                    # state.candles_4h = cleanup_candles(state.candles_4h, 7) #coment-out for backtesting older than 7 days

                    #coloring and ordering candles
                    if len(state.candles_4h) > 4:
                        color_order(state.candles_4h)
                        
                        if not has_open_position("BTCUSDT"):
                        
                            #preps for order algorithm
                            if (state.candles_4h[-1].color == "green") and (state.candles_4h[-1].order >= 1) and (state.candles_4h[-3].color == "red" or state.candles_4h[-2].color == "red"):
                                state.entry_price, state.stop_price = state.candles_4h[-1].high + 1, state.candles_4h[-1].low - 1
                                state.trailing_stop_price = state.candles_4h[-1].low - 1
                                state.buy_amount = set_buy_ammount(state)
                                state.start_buy = True
                                print("#########################################################")
                                print(f"Found 4h candle green or: 1, at {state.candles_4h[-1]}")
                                print(f"Setting entry price to {state.entry_price}")
                                print(f"Setting stop price to {state.stop_price}")
                                print(f"Setting buy amount to {state.buy_amount}")
                                print(f"Setting start_buy to {state.start_buy}")
                                print("#########################################################")
                            elif ((state.candles_4h[-1].color == "green") and (state.candles_4h[-1].order == 3)) or state.candles_4h[-1].color == "red":
                                    state.start_buy = False

                                    print(f"Found 4h candle at {state.candles_4h[-1]}")
                                    print(f"Setting start_buy to {state.start_buy}")


            #buy algorithm, every minute
            if state.start_buy:
                if not has_open_position("BTCUSDT") and (state.entry_price - 1 < state.active_candle_1m.close) and (state.candles_1d[-1].color == "green") and (state.candles_1d[-1].order >= 2):
                    print(f"has_open position = {has_open_position('BTCUSDT')}")
                    state.balance_saved = float(query_balance_free("USDT"))
                    order_market_value(symbol = "BTCUSDT", value = state.buy_amount)
                    state.trailing_unrealized_pnl = 0
                    state.start_buy = False

                    print(f"The last 4h candle has set the entry price to:") 
                    print(f"{state.entry_price} and this - 1 is less than active candle close {state.active_candle_1m.close}")
                    print(f"Yesterday's 1d candle was {state.candles_1d[-1].color} and it's order was {state.candles_1d[-1].order}, which is >= 2")
                    print(f"State active candle is {state.active_candle_1m}")
                    print("#########################################################")
                    print(f"Bought {state.buy_amount / state.active_candle_1m.close} BTC at market spending {state.buy_amount} USDT")
                    print("#########################################################")
                    print(f"Setting stop price to {state.stop_price}")
                    print(f"Setting trailing unrealised pnl to {state.trailing_unrealized_pnl}")
                    print(f"Setting start_buy to {state.start_buy}")
                    
                    
                    
            #sell algorithm, every minute
            if has_open_position("BTCUSDT"):  
                state.has_position = query_open_position_by_symbol(symbol = "BTCUSDT", include_dust = True)
                print(f"position pnl {state.has_position.unrealized_pnl}")
            
                if data.price_last <= state.trailing_stop_price:
                    print(f"BTC price is  {data.price_last} <= than trailing stop price ({state.trailing_stop_price})")
                    print(f"Selling BTC at {state.active_candle_1m.close}")
                    close_position(symbol="BTCUSDT")
                      
                elif state.has_position.unrealized_pnl >= (state.balance_saved * 0.009985)  * 1.2:
    
                    if state.has_position.unrealized_pnl > state.trailing_unrealized_pnl:
                        print(f"Unrealized pnl ({state.has_position.unrealized_pnl}) is greater than trailing unrealized pnl({state.trailing_unrealized_pnl})")
                        state.trailing_stop_price = data.price_last * 0.9836
                        print(f"Setting trailing stop price to {state.trailing_stop_price}")
                        state.trailing_unrealized_pnl = float(state.has_position.unrealized_pnl)
                        print(f"Setting trailing unrealized pnl to {state.trailing_unrealized_pnl}. Our active candle is {state.active_candle_1m}")
                
                elif (state.stop_price + 1 > state.active_candle_1m.close):
                    print("Our State stop price({state.stop_price}) +1 is greater than close of active candle ({state.active_candle_1m.close})")
                    close_position(symbol="BTCUSDT")
                    print("We have sold our BTC according to code line 179.")
                
                elif hour_passed(state.has_position, state.active_candle_1m) and state.active_candle_1m.close < state.candles_4h[-4].close:
                    print(f"More than an hour has passed since we bought BTC and we fear that the current 4h candle is turning red.")
                    print(f"Meaning that close active candle = {state.active_candle_1m.close}, which is less than close of -4th 4h candle ({state.candles_4h[-4].close})")
                    close_position(symbol="BTCUSDT")
                    print("We have sold our BTC according to code line 185.")

                
        
@schedule(interval="1d", symbol="BTCUSDT", window_size = 14)
def daily(state, data):
    if not state.candles_1d:
        for t, o, h, l, c, v in zip(data.times, data.open.select("open"), data.high.select("high"),
        data.low.select("low"), data.close.select("close"), data.volume.select("volume")):
            candle_time = datetime.fromtimestamp(t // 1000, pytz.UTC)
            state.candles_1d.append(candle(candle_time, o, h, l, c, v, "1d"))
        for i in range(5, len(state.candles_1d) + 1):
            color_order(state.candles_1d[:i])
        
    else:
        last_candle = datetime.fromtimestamp(data.last_time // 1000, pytz.UTC)
        state.candles_1d.append(set_candle(last_candle, "1d", data = data))
        color_order(state.candles_1d)

@schedule(interval="1h", symbol="BTCUSDT", window_size = 1)
def hourly(state, data):
    pass
