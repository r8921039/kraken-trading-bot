#!/usr/bin/env python3

import argparse
from lib import *

market_mode = "bull"
leverage = "5:1"
refresh_time = 30
# 1d: 86400
# 1h: 3600 
adj_wait_secs = 2 * 3600 
buy_discount_rate = 0.98
sell_to_curr_gap = Decimal(1.5)
sell_to_buy_gap = Decimal(1)
curr_to_buy_gap = Decimal(1)
buy_offset = 50
max_buy_price = 19000 + buy_offset 
min_buy_price = 6000 + buy_offset 
sell_step = 35
buy_step = 100

def get_target_buy_price():
    target_price = (Decimal(ave_price) + Decimal(curr_price)) / 2
    #target_price = Decimal(ave_price)
    #target_price = Decimal(curr_price)
    return round(target_price * Decimal(buy_discount_rate) / buy_step) * buy_step + buy_offset

def get_target_sell_price():
    return get_target_buy_price() + sell_to_buy_gap * buy_step

parser = argparse.ArgumentParser(description='bot args: <sell_price>/<sell_step>/<buy_step>')
ticker = get_ticker()
if (ticker == TypeError):
    sys.exit()
else:
    curr_price = ticker['price']
    ave_price = ticker['ave']
    sell_price = get_target_sell_price()
parser.add_argument('-sp', '-s', '-p', default=sell_price, type=int, help='sell price (default: %s)' % sell_price)
parser.add_argument('-ss', default=sell_step, type=int, help='sell step (default: %s)' % sell_step)
parser.add_argument('-bs', default=buy_step, type=int, help='buy step (default: %s)' % buy_step)
args = parser.parse_args()
sell_price = args.sp
sell_step = args.ss
buy_step = args.bs
#print(sell_price)
#print(sell_step)
#print(buy_step)
#sys.exit()

buy_price = Decimal(sell_price - sell_to_buy_gap * buy_step)

tot_order_vol = Decimal((buy_price - min_buy_price) / buy_step + 1)

print()
print("args: <sell_price> <sell_step> <buy_step>")
print()
print("{:<20s}{:>15.0f}".format("SELL PRICE", sell_price))
print("{:<20s}{:>15.0f}".format("SELL STEP", sell_step))
print()
print("{:<20s}{:>15.0f}".format("BUY PRICE", buy_price))
print("{:<20s}{:>15.0f}".format("BUY STEP", buy_step))
print()
print("{:<20s}{:>15.0f}".format("BUY PRICE MAX", max_buy_price))
print("{:<20s}{:>15.0f}".format("BUY PIRCE MIN", min_buy_price))
print()
print("{:<20s}{:>15.0f}".format("TOTAL ORDER VOL", tot_order_vol))
print()
print("Press <enter> to continue or 'n' to cancel (y/n)?")
yn = sys.stdin.read(1)
if (yn == 'n' or yn == 'N'):
    sys.exit()
else:
    os.system('clear')

#
# main
#

first_time = True
while True:
    if (first_time):
        first_time = False
    else:
        for i in range(1, refresh_time):
            time.sleep(1)
            print(".", end =" ", flush=True)
        print("")
        os.system('clear')
    print('='*80)
    print("KRAKEN TRADING BOT %s" % datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y"))
    print("{:<20s}{:>15.0f}{:>15.0f}".format("TARGET SELL/BUY", sell_price, buy_price))
    print('='*80)

    #
    # open positions
    #
    
    pos = get_pos()
    if (pos == TypeError):
        continue
    #show_pos(pos)
    pos_vol, pos_type = get_pos_vol(pos)
    
    #
    # ticker
    #
    ticker = get_ticker()
    if (ticker == TypeError):
        continue
    show_ticker(ticker)
    curr_price = ticker['price']
    ave_price = ticker['ave'] 

    #
    # open orders
    #
    ol_k, ol_v = get_open_orders()
    if (ol_k == TypeError or ol_v == TypeError):
        continue

    # sell
    next_sell_k, next_sell_v = get_next_sell(ol_k, ol_v)
    show_next_sell(next_sell_k, next_sell_v)
    
    tot_sell = get_total_sell(ol_v)
    show_total_sell(tot_sell)
   
    #print()

    # buy
    next_buy_k, next_buy_v = get_next_buy(ol_k, ol_v)
    show_next_buy(next_buy_k, next_buy_v)
    
    tot_buy = get_total_buy(ol_v)
    show_total_buy(tot_buy)
    
    #
    # open positions (double check to ensure data doesn't change)
    #
    
    pos2 = get_pos()
    #show_pos(pos2)
    if (pos2 == TypeError):
        continue
    pos2_vol, pos2_type = get_pos_vol(pos2)
    
    if (not same_pos(pos, pos2)):
        print("\033[93mWARN!! Position inconsistent! Better double check!")
        continue
   
    # adjust total orders
    if (Decimal(tot_buy) > tot_order_vol):
        delete_order(next_buy_k, next_buy_v) 
        continue
    if (Decimal(tot_sell) > tot_order_vol):
        delete_order(next_sell_k, next_sell_v)
        continue
    # adjust next sell price lower
    if (next_sell_v != None):
        curr_sell_price = Decimal(next_sell_v['descr']['price'])
        #print("\033[93mINFO!! Next sell order elapsed %s (sec) \033[00m" % (Decimal(time.time()) - Decimal(next_sell_v['opentm'])))
        if (Decimal(time.time()) - Decimal(next_sell_v['opentm']) > adj_wait_secs 
                and curr_sell_price - sell_to_curr_gap * Decimal(sell_step) > Decimal(curr_price)):
            new_sell_price = curr_sell_price - Decimal(sell_step)
            new_sell_vol = Decimal(next_sell_v['vol']) - Decimal(next_sell_v['vol_exec'])
            delete_order(next_sell_k, next_sell_v)
            add_orders("sell", new_sell_price, 0, 1, new_sell_vol, leverage, False)
            print("\033[93mINFO!! Lower next sell price/volume to %s %s \033[00m" % (new_sell_price, new_sell_vol))
            continue
    # adjust target buy price higher based on ave_price/curr_price
    new_target_buy_price = get_target_buy_price()
    if (next_sell_v == None 
            #and Decimal(time.time()) - Decimal(next_buy_v['opentm']) > adj_wait_secs 
            and new_target_buy_price > buy_price):
        if (new_target_buy_price <= max_buy_price):
            buy_price = new_target_buy_price 
            sell_price = Decimal(buy_price + sell_to_buy_gap * buy_step)
            tot_order_vol = Decimal((buy_price - min_buy_price) / buy_step + 1)
            print("\033[93mINFO!! Higher sell_price/buy_price/tot_volume to %s %s %s \033[00m" % (sell_price, buy_price, tot_order_vol))
            continue
        else:
            print("\033[93mINFO!! Max buy price %s reached. Won't adjust higher. \033[00m" % max_buy_price)

    delta_sell_vol = Decimal(pos_vol) - Decimal(tot_sell)
    if (delta_sell_vol < 0):
        print("\033[91mERROR!! Open sell order volume > open positions! Abort!!\033[00m")
        print("\033[91m{:<30s}{:>20.8f}\033[00m".format("Total open position volume", pos_vol))
        print("\033[91m{:<30s}{:>20.8f}\033[00m".format("Total open sell order volume", tot_sell))
        print("\033[91m{:<30s}{:>20.8f}\033[00m".format("Delta", delta_sell_vol))
        sys.exit()    

    # with open positions - shall we add more sell
    if (delta_sell_vol > 0):
        # cap new sell volume
        if (delta_sell_vol > 1):
            order_vol = 1
        else:
            order_vol = delta_sell_vol
    
        # determine new sell price
        if (next_sell_v == None):
            new_sell_price = sell_price - Decimal(sell_step)
        else:
            if (Decimal(next_sell_v['vol']) >= 1):
                new_sell_price = Decimal(next_sell_v['descr']['price']) - Decimal(sell_step)
            else:
                new_sell_price = Decimal(next_sell_v['descr']['price'])
    
        if (Decimal(new_sell_price) > Decimal(curr_price)):
            order_price = Decimal(new_sell_price)
        else:
            order_price = round(Decimal(curr_price)) + Decimal(sell_step)
    
        add_orders("sell", order_price, 0, 1, order_vol, leverage, False)
    
    # add more buy
    delta_buy_vol = tot_order_vol - Decimal(tot_buy) - Decimal(pos_vol)
    if (delta_buy_vol > 0):
        # cap new buy volume
        if (delta_buy_vol > 1):
            order_vol = 1
        else:
            order_vol = delta_buy_vol
    
        # determine new buy price
        if (next_buy_v == None):
            print("\033[93mWARN!! No buy order detected. Almost impossible!! Abort!!\033[00m")
            sys.exit()
        else:
            new_buy_price = Decimal(next_buy_v['descr']['price']) + Decimal(buy_step)
    
        if (Decimal(curr_price) - curr_to_buy_gap * Decimal(buy_step) > Decimal(new_buy_price)):
            order_price = Decimal(new_buy_price)
            add_orders("buy", order_price, 0, 1, order_vol, leverage, False)
        else:
            print("\033[93mINFO!! New target buy price %s is too close to the current price. Skip this time!\033[00m" % new_buy_price)
    
    #
    # show pos and balance
    #
    
    tot_fee = 0
    tot_fee = show_pos(pos)
    show_trade_balance(tot_fee)
    show_balance()





