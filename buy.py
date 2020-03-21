#!/usr/bin/env python3

from lib import *

#pos_k, pos_v = get_open_positions()
#show_open_positions(pos_k, pos_v)
#show_trade_balance()

order_type="buy"
start_price = -1000000
step_price = -100
order_count = 1
order_size = 1
leverage="5:1"
dry_run = False

if (len(sys.argv) > 1):
    start_price = int(sys.argv[1])

if (len(sys.argv) > 2):
    order_count = int(sys.argv[2])

if (len(sys.argv) > 3):
    dry_run = bool(sys.argv[3])

### WARNING!!! it fails between 701000 and 702000, likely too big a number
add_orders(order_type, start_price + 1, step_price, order_count, order_size, leverage, dry_run) 
os.system("clikraken ol | grep {}".format(order_type))
os.system("echo 'NUMBER OF ENTRIES: '")
os.system("clikraken ol | grep {} | wc -l".format(order_type))
