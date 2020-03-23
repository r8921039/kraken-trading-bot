#!/usr/bin/env python3

from lib import *

#
# ticker
#
ticker = get_ticker()
show_ticker(ticker)

#
# open orders
#
ol = get_open_orders()

# sell
sell_n = get_next_sell(ol)
show_next_sell(sell_n)

sell_t = get_total_sell(ol)
show_total_sell(sell_t)

# buy
buy_n = get_next_buy(ol)
show_next_buy(buy_n)

buy_t = get_total_buy(ol)
show_total_buy(buy_t)

#
# open positions
#

pos = get_pos()
show_pos(pos)

#
# balance
#

show_trade_balance()
show_balance()
