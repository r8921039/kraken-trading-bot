#!/usr/bin/env python3

#
# this trade.py is meant to be executed from buy.py/sell.py
#

import argparse
from lib import *

#pos_k, pos_v = get_open_positions()
#show_open_positions(pos_k, pos_v)
#show_trade_balance()

start_price = -1000000
step_price = 0
order_count = 1
order_vol = 1
leverage = "5:1"
#leverage = "none"
dry_run = False

parser = argparse.ArgumentParser(description='trade args: <start_price> <order_volume> <step_price> <order_count> <dry_run>')
parser.add_argument('-p', default=start_price, type=int, required=True, help='start price (default: %s)' % start_price)
parser.add_argument('-s', default=step_price, type=int, help='step price (default: %s)' % step_price)
parser.add_argument('-c', default=order_count, type=int, help='order count (default: %s)' % order_count)
parser.add_argument('-v', default=order_vol, type=int, help='order volume (default: %s)' % order_vol)
parser.add_argument('-l', default=leverage, type=str, help='leverage (default: %s)' % leverage)
parser.add_argument('-d', default=dry_run, action='store_true', help='dry run (default: %s)' % dry_run)
args = parser.parse_args()
start_price = args.p
step_price = args.s
order_count = args.c
order_vol = args.v
leverage = args.l
dry_run = args.d

order_type = sys.argv[0].split('/')[-1].split('.py')[0]
if (order_type != "buy" and order_type != "sell"):
    print("\033[91mERROR! Must be executed thru sell.py/buy.py. Abort!\033[00m")
    sys.exit()
print()
print("args: <start_price> <order_volume> <step_price> <order_count> <leverage> <dry_run>")
print()
print("{:<30s}{:>20s}".format("order type", order_type))
print("{:<30s}{:>20.0f}".format("start price", start_price))
if (step_price < 0):
    print("{:<30s}{:>20.0f}".format("step price", step_price))
if (order_count > 1):
    print("{:<30s}{:>20.0f}".format("count", order_count))
print("{:<30s}{:>20.8f}".format("volume", order_vol))
if (leverage != "5:1"):
    print("{:<30s}{:>20s}".format("leverage", leverage))
if (dry_run):
    print("{:<30s}{:>20s}".format("dry run", str(dry_run)))
print()
print("Press <enter> to continue or 'n' to cancel (y/n)?") 
yn = sys.stdin.read(1)
if (yn == 'n' or yn == 'N'):
    sys.exit()
else:
    ### CAUTION!!! it fails between 701000 and 702000, likely too big a number
    add_orders(order_type, start_price, step_price, order_count, order_vol, leverage, dry_run) 

os.system("clikraken ol | grep {}".format(order_type))
os.system("echo 'NUMBER OF ENTRIES: '")
os.system("clikraken ol | grep {} | wc -l".format(order_type))

