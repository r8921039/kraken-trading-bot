#!/usr/bin/env python3

from lib import *

SELL_PRICE = 6100
SELL_STEP = 30
BUY_PRICE = 5900
BUY_STEP = 100
TOTAL_ORDER_VOLUME = 60
LEVERAGE = "5:1"

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
#show_ticker(ticker)
curr_price = ticker['price']

#
# open orders
#
ol = get_open_orders()

# sell
next_sell = get_next_sell(ol)
#show_next_sell(next_sell)

tot_sell = get_total_sell(ol)
#show_total_sell(tot_sell)

# buy
next_buy = get_next_buy(ol)
#show_next_buy(next_buy)

tot_buy = get_total_buy(ol)
#show_total_buy(tot_buy)

#
# open positions (double check to ensure data doesn't change)
#

pos2 = get_pos()
#show_pos(pos)

if (not same_pos(pos, pos2)):
    print("WARN!! position change detected. Abort for now and try again later!")
    sys.exit()

delta_sell_vol = Decimal(pos_vol) - Decimal(tot_sell)
if (delta_sell_vol < 0):
    print("ERROR!! ope0in sell order vol > open positions! Abort!!")
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

    if (Decimal(curr_price) > Decimal(base_price)):
        order_price = Decimal(base_price)
    else:
        order_price = Decimal(curr_price) - Decimal(BUY_STEP)

    add_orders("buy", order_price, 0, 1, order_vol, LEVERAGE, False)
 

#
# balance
#

#show_trade_balance()
#show_balance()
