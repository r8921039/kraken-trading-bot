#!/usr/bin/env python3
    
from lib import *

SELL_PRICE = 6100
SELL_STEP = 60
BUY_PRICE = 5900
BUY_STEP = 100
TOTAL_ORDER_VOLUME = 60
LEVERAGE = "5:1"
REFRESH_TIME = 30

if (len(sys.argv) > 1):
    SELL_PRICE = int(sys.argv[1])

if (len(sys.argv) > 2):
    SELL_STEP = abs(int(sys.argv[2]))

if (len(sys.argv) > 3):
    BUY_PRICE = int(sys.argv[3])

if (len(sys.argv) > 4):
    BUY_STEP = abs(int(sys.argv[4]))

if (len(sys.argv) > 5):
    TOTAL_ORDER_VOLUME = int(sys.argv[5])

print()
print("args: <sell_price> <sell_step> <buy_price> <buy_step> <total_order_volume>")
print()
print("{:<30s}{:>20.0f}".format("SELL PRICE", SELL_PRICE))
print("{:<30s}{:>20.0f}".format("SELL STEP", SELL_STEP))
print("{:<30s}{:>20.0f}".format("BUY  PRICE", BUY_PRICE))
print("{:<30s}{:>20.0f}".format("BUY  STEP", BUY_STEP))
print("{:<30s}{:>20.0f}".format("TOTAL ORDER VOL", TOTAL_ORDER_VOLUME))
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
        for i in range(1, REFRESH_TIME):
            time.sleep(1)
            print(".", end =" ", flush=True)
        print("")
        os.system('clear')
    print('='*60)
    print("KRAKEN TRADING BOT %s" % datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y"))
    print('='*60)

    #
    # open positions
    #
    
    pos = get_pos()
    #show_pos(pos)
    pos_vol, pos_type = get_pos_vol(pos)
    
    #
    # ticker
    #
    ticker = get_ticker()
    show_ticker(ticker)
    curr_price = ticker['price']
    
    #
    # open orders
    #
    ol = get_open_orders()
    
    # sell
    next_sell = get_next_sell(ol)
    show_next_sell(next_sell)
    
    tot_sell = get_total_sell(ol)
    show_total_sell(tot_sell)
   
    print()

    # buy
    next_buy = get_next_buy(ol)
    show_next_buy(next_buy)
    
    tot_buy = get_total_buy(ol)
    show_total_buy(tot_buy)
    
    #
    # open positions (double check to ensure data doesn't change)
    #
    
    pos2 = get_pos()
    #show_pos(pos2)
    pos2_vol, pos2_type = get_pos_vol(pos2)
    
    if (not same_pos(pos, pos2)):
        print("WARN!! Position inconsistent! Better double check!")
        continue
    
    delta_sell_vol = Decimal(pos_vol) - Decimal(tot_sell)
    if (delta_sell_vol < 0):
        print("ERROR!! Open sell order volume > open positions! Abort!!")
        print("{:<30s}{:>20.8f}".format("Total open position volume", pos_vol))
        print("{:<30s}{:>20.8f}".format("Total open sell order volume", tot_sell))
        print("{:<30s}{:>20.8f}".format("Delta", delta_sell_vol))
        sys.exit()
    
    # with open positions
    if (delta_sell_vol > 0):
        # cap new sell volume
        if (delta_sell_vol > 1):
            order_vol = 1
        else:
            order_vol = delta_sell_vol
    
        # determine new sell price
        if (next_sell == None):
            base_price = SELL_PRICE
        else:
            base_price = Decimal(next_sell['descr']['price']) - Decimal(SELL_STEP)
    
        if (Decimal(curr_price) < Decimal(base_price)):
            order_price = Decimal(base_price)
        else:
            order_price = Decimal(curr_price) + Decimal(SELL_STEP)
    
        add_orders("sell", order_price, 0, 1, order_vol, LEVERAGE, False)
    
    
    delta_buy_vol = TOTAL_ORDER_VOLUME - Decimal(tot_buy) - Decimal(pos_vol)
    if (delta_buy_vol > 0):
        # cap new buy volume
        if (delta_buy_vol > 1):
            order_vol = 1
        else:
            order_vol = delta_buy_vol
    
        # determine new buy price
        if (next_buy == None):
            #base_price = BUY_PRICE
            print("WARN!! No buy order detected. Almost impossible!! Abort!!")
            sys.exit()
        else:
            base_price = Decimal(next_buy['descr']['price']) + Decimal(BUY_STEP)
    
        if (Decimal(curr_price) > Decimal(base_price) + Decimal(BUY_STEP)):
            order_price = Decimal(base_price)
            add_orders("buy", order_price, 0, 1, order_vol, LEVERAGE, False)
        #else:
        #    print("INFO!! Current price is too close. Skip this time.")
        #    order_price = Decimal(curr_price) - Decimal(BUY_STEP)
    
     
    
    #
    # balance
    #
    
    show_trade_balance()
    show_balance()
