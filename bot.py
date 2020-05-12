#!/usr/bin/env python3

import argparse
from lib import *

market_mode = "bull"
leverage = "5:1"
refresh_time = 30
# 6h: 21600 = (86400 / 4)
adj_wait_secs = 21600 
discount_rate = 0.93
#discount_rate = 0.96
sell_to_curr_premium = 2
sell_to_buy_premium = 2
curr_to_buy_premium = 1
min_buy_price = 6050 

parser = argparse.ArgumentParser(description='bot args: <sell_price>/<sell_step>/<buy_step>')
ticker = get_ticker()
sell_step = 80
buy_step = 100
if (ticker == TypeError):
    sys.exit()
else:
    #sell_price = round(Decimal(ticker['price']) / buy_step) * buy_step
    sell_price = round(Decimal(ticker['ave']) / buy_step) * buy_step
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

buy_price = Decimal(sell_price - sell_to_buy_premium * buy_step)

tot_order_vol = Decimal((buy_price - min_buy_price) / buy_step + 1)

print()
print("args: <sell_price> <sell_step> <buy_step>")
print()
print("{:<20s}{:>15.0f}".format("SELL PRICE", sell_price))
print("{:<20s}{:>15.0f}".format("SELL STEP", sell_step))
print("{:<20s}{:>15.0f}".format("BUY  PRICE MAX", buy_price))
print("{:<20s}{:>15.0f}".format("BUY  STEP", buy_step))
print("{:<20s}{:>15.0f}".format("BUY  PIRCE MIN", min_buy_price))
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
    if (next_sell_v != None 
            and Decimal(time.time()) - Decimal(next_sell_v['opentm']) > adj_wait_secs 
            and Decimal(next_sell_v['descr']['price']) > Decimal(ave_price) 
            and Decimal(next_sell_v['descr']['price']) > Decimal(curr_price) + sell_to_curr_premium * Decimal(sell_step)):
        tmp_price = Decimal(next_sell_v['descr']['price']) - Decimal(sell_step)
        tmp_vol = Decimal(next_sell_v['vol']) - Decimal(next_sell_v['vol_exec'])
        delete_order(next_sell_k, next_sell_v)
        add_orders("sell", tmp_price, 0, 1, tmp_vol, leverage, False)
        print("\033[91mINFO!! Lower next sell price/volume to %s %s \033[00m" % (tmp_price, tmp_vol))
        continue
    if (next_sell_v == None 
            #and Decimal(time.time()) - Decimal(next_buy_v['opentm']) > adj_wait_secs 
            and round(Decimal(ave_price) * Decimal(discount_rate) / buy_step) * buy_step > buy_price):
        buy_price = round(Decimal(ave_price) * Decimal(discount_rate) / buy_step) * buy_step
        sell_price = Decimal(buy_price + sell_to_buy_premium * buy_step)
        tot_order_vol = Decimal((buy_price - min_buy_price) / buy_step + 1)
        print("\033[91mINFO!! Higher sell_price/buy_price/tot_volume to  %s %s %s \033[00m" % (sell_price, buy_price, tot_order_vol))
        continue

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
            base_price = sell_price
        else:
            base_price = Decimal(next_sell_v['descr']['price']) - Decimal(sell_step)
    
        if (Decimal(curr_price) < Decimal(base_price)):
            order_price = Decimal(base_price)
        else:
            order_price = round(Decimal(curr_price)) + Decimal(sell_step)
    
        add_orders("sell", order_price, 0, 1, order_vol, leverage, False)
    

    # with or without open positions - shall we add more buy
    delta_buy_vol = tot_order_vol - Decimal(tot_buy) - Decimal(pos_vol)
    if (delta_buy_vol > 0):
        # cap new buy volume
        if (delta_buy_vol > 1):
            order_vol = 1
        else:
            order_vol = delta_buy_vol
    
        # determine new buy price
        if (next_buy_v == None):
            #base_price = buy_price
            print("\033[93mWARN!! No buy order detected. Almost impossible!! Abort!!\033[00m")
            sys.exit()
        else:
            base_price = Decimal(next_buy_v['descr']['price']) + Decimal(buy_step)
    
        if (Decimal(curr_price) > Decimal(base_price) + curr_to_buy_premium * Decimal(buy_step)):
            order_price = Decimal(base_price)
            add_orders("buy", order_price, 0, 1, order_vol, leverage, False)
        #else:
        #    print("\033[93mINFO!! Current price is too close. Skip this time!\033[00m")
        #    order_price = Decimal(curr_price) - Decimal(buy_step)
    
     
    
    #
    # show pos and balance
    #
    
    show_pos(pos)
    #print()
    show_trade_balance()
    #print()
    show_balance()
