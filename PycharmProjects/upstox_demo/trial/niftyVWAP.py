from upstox_api.api import *
from datetime import datetime
from threading import Timer
import math

#Api key , access token
u = Upstox ('JMJueJYcG05yrycTa4tBX3zP5KGqOl2c8dAZ31Ay', '117dcb1f1ff0ec2def5b73ab14f5e5a61a825a42')

u.get_master_contract('NSE_FO') # get contracts for NSE FO
u.get_master_contract('NSE_INDEX') # get contracts for NSE_INDEX


india_vix_nse_index = u.get_instrument_by_symbol('NSE_INDEX', 'INDIA_VIX')
nifty_nse_future = u.get_instrument_by_symbol('NSE_FO', 'nifty17decfut')

today=datetime.today()

fetch_open_time=today.replace(day=today.day + 1, hour=9, minute=52, second=0, microsecond=0)
calculate_prices_time=today.replace(day=today.day + 1, hour=9, minute=52, second=5, microsecond=0)
buy_order_time=today.replace(day=today.day + 1, hour=9, minute=52, second=7, microsecond=0)

delta_t= fetch_open_time - today
delta_t_calculation = calculate_prices_time - today
delta_t_order_place = buy_order_time - today
time_for_open_prices= delta_t.seconds + 1
time_for_calculation = delta_t_calculation.seconds + 1
time_for_order = delta_t_order_place.seconds+1

india_vix_open=0
nifty_open= 0
buy_above=0.0
buy_target=0.0
sl_for_buy=0.0
sell_below=0.0
sell_target=0.0
sl_for_sell=0.0

def fetch_open_prices():
    india_vix = u.get_live_feed(india_vix_nse_index, LiveFeedType.Full)
    global india_vix_open
    india_vix_open = india_vix["open"]
    nifty_nse_future_full = u.get_live_feed(nifty_nse_future, LiveFeedType.Full)
    global nifty_open
    nifty_open = nifty_nse_future_full["open"]
    print "nifty open "
    print nifty_open
    print "vix open"
    print india_vix_open



def calculate_target_and_sl():
    first_sd = nifty_open * india_vix_open * 0.00104684784518
    global buy_above
    buy_above = 0.236 * first_sd + nifty_open
    buy_above = math.ceil(buy_above)
    global buy_target
    buy_target = 0.382 * first_sd + nifty_open
    buy_target = math.ceil(buy_target)
    global sl_for_buy
    sl_for_buy = nifty_open - 1
    sl_for_buy = math.ceil(sl_for_buy)
    global sell_below
    sell_below = nifty_open - 0.236 * first_sd
    sell_below = math.ceil(sell_below)
    global sell_target
    sell_target = nifty_open - 0.382 * first_sd
    sell_target=math.ceil(sell_target)
    global sl_for_sell
    sl_for_sell = nifty_open + 1
    sl_for_sell = math.ceil(sl_for_sell)
    print buy_above
    print buy_target
    print sl_for_buy
    print sell_below
    print sell_target
    print sl_for_sell

def place_nifty_buy_order():
    print "####################### Buy order ###################"
    print (u.place_order(TransactionType.Buy,  # transaction_type
                  nifty_nse_future,  # instrument
                  75,  # quantity
                  OrderType.StopLossMarket,  # order_type
                  ProductType.Intraday,  # product_type
                  0.0,  # price
                  float(buy_above),  # trigger_price
                  0,  # disclosed_quantity
                  DurationType.DAY,  # duration
                  0.0,  # stop_loss
                  0.0,  # square_off
                  None)  # trailing_ticks
           )

def place_nifty_buy_target_order():
    print "####################### Buy target order ###################"
    print (u.place_order(TransactionType.Sell,  # transaction_type
                  nifty_nse_future,  # instrument
                  75,  # quantity
                  OrderType.StopLossMarket,  # order_type
                  ProductType.Intraday,  # product_type
                  float(buy_target),  # price
                  None,  # trigger_price
                  0,  # disclosed_quantity
                  DurationType.DAY,  # duration
                  0.0,  # stop_loss
                  0.0,  # square_off
                  None)  # trailing_ticks
           )

def stop_loss_order_for_buy():
    print "####################### stop loss for buy ###################"
    print (u.place_order(TransactionType.Sell,  # transaction_type
                         nifty_nse_future,  # instrument
                         75,  # quantity
                         OrderType.StopLossMarket,  # order_type
                         ProductType.Intraday,  # product_type
                         0.0,  # price
                         float(sl_for_buy),  # trigger_price
                         0,  # disclosed_quantity
                         DurationType.DAY,  # duration
                         None,  # stop_loss
                         None,  # square_off
                         None)  # trailing_ticks
           )

def place_nifty_sell_order():
    print "####################### Sell order ###################"
    u.place_order(TransactionType.Sell,  # transaction_type
                  nifty_nse_future,  # instrument
                  75,  # quantity
                  OrderType.Limit,  # order_type
                  ProductType.Intraday,  # product_type
                  float(sell_below),  # price
                  None,  # trigger_price
                  0,  # disclosed_quantity
                  DurationType.DAY,  # duration
                  float(sl_for_sell),  # stop_loss
                  float(sell_target),  # square_off
                  None)  # trailing_ticks

def place_nifty_sell_order():
    print "####################### Sell target order ###################"
    u.place_order(TransactionType.Buy,  # transaction_type
                  nifty_nse_future,  # instrument
                  75,  # quantity
                  OrderType.Limit,  # order_type
                  ProductType.Intraday,  # product_type
                  float(sell_below),  # price
                  None,  # trigger_price
                  0,  # disclosed_quantity
                  DurationType.DAY,  # duration
                  float(sl_for_sell),  # stop_loss
                  float(sell_target),  # square_off
                  None)  # trailing_ticks

def buy_order_triggered_event_handler (event):
    print ("Event: %s" % str(event))
    stop_loss_order_for_buy()
    # if (event['aa'] == 'aa'):
    # return

#
# def event_handler_quote_update(message):
#     print "Last Trade price: %s" % str(message['ltp'])
#     print("Quote Update: %s" % str(message))



open_price_timer = Timer(time_for_open_prices, fetch_open_prices)
open_price_timer.start()

target_set_timer = Timer(time_for_calculation, calculate_target_and_sl)
target_set_timer.start()

place_buy_order_set_timer = Timer(time_for_order, place_nifty_buy_order)
place_buy_order_set_timer.start()



###################### subscribe to price change event ##################

# u.set_on_quote_update(event_handler_quote_update)
u.unsubscribe(nifty_nse_future,LiveFeedType.LTP)
u.subscribe(nifty_nse_future, LiveFeedType.LTP)

###################### subscribe to buy order trigger event ##################
# u.set_on_order_update (buy_order_triggered_event_handler)
u.set_on_trade_update(buy_order_triggered_event_handler)
u.start_websocket (False)

# place_sell_order_set_timer = Timer(time_for_order, place_nifty_sell_order)
# place_sell_order_set_timer.start()