#!/usr/bin/env python3

from lib import *

#
# main
#

### WARNING!!! it fails between 701000 and 702000, likely too big a number
###create_order("sell", 701000, 702000, 100)

#pos_k, pos_v = get_open_positions()
#show_open_positions(pos_k, pos_v)
#get_trade_balance()

delete_orders("sell")
add_orders("sell", 5400, 5701, 50)
#os.system("clikraken ol | grep sell")

