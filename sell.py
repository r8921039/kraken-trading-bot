#!/usr/bin/env python3

from lib import *

type="sell"

### WARNING!!! it fails between 701000 and 702000, likely too big a number
###create_order(type, 701000, 702000, 100)

#pos_k, pos_v = get_open_positions()
#show_open_positions(pos_k, pos_v)
#get_trade_balance()

#delete_orders(type)
# add_orders(<type>, <start_price>, <step_price>, <order_count>, <order_size>, <leverage>, <dry_run>)
add_orders(type, 6999, 100, 1, 1, "5:1", False) 
os.system("clikraken ol | grep {}".format(type))
os.system("echo 'NUMBER OF ENTRIES: '")
os.system("clikraken ol | grep {} | wc -l".format(type))
