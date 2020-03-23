#!/usr/bin/env python3

#
# this trade.py is meant to be executed from buy.py/sell.py
#

from lib import *

#pos_k, pos_v = get_open_positions()
#show_open_positions(pos_k, pos_v)
#show_trade_balance()

start_price = -1000000
step_price = 0
order_count = 1
order_vol = 1
leverage = "5:1"
dry_run = False

if (len(sys.argv) > 1):
    start_price = int(sys.argv[1])

if (len(sys.argv) > 2):
    order_vol = float(sys.argv[2])

if (len(sys.argv) > 3):
    step_price = abs(int(sys.argv[3]))

if (len(sys.argv) > 4):
    order_count = int(sys.argv[4])

if (len(sys.argv) > 5):
    dry_run = bool(sys.argv[5])

order_type = sys.argv[0].split('/')[-1].split('.py')[0]
    # nada
if (order_type == "buy"):
    step_price = 0 - step_price
elif (order_type != "sell"):
    print("ERROR! Must be executed thru sell.py/buy.py. Exit!")
    sys.exit()
print()
print("args: <start_price> <order_volume> <step_price> <order_count> <dry_run>")
print()
print("{:<30s}{:>20s}".format("order type", order_type))
print("{:<30s}{:>20.0f}".format("start price", start_price))
if (step_price > 0):
    print("{:<30s}{:>20.0f}".format("step price", step_price))
if (order_count > 1):
    print("{:<30s}{:>20.0f}".format("count", order_count))
print("{:<30s}{:>20.8f}".format("volume", order_vol))
#print("{:<30s}{:>20s}".format("leverage", leverage))
if (dry_run):
    print("{:<30s}{:>20s}".format("dry run", str(dry_run)))
print()
print("press <enter> to continue or 'n' to cancel (y/n)?") 
yn = sys.stdin.read(1)
if (yn == 'n' or yn == 'N'):
    sys.exit()
else:
    ### WARNING!!! it fails between 701000 and 702000, likely too big a number
    add_orders(order_type, start_price, step_price, order_count, order_vol, leverage, dry_run) 

os.system("clikraken ol | grep {}".format(order_type))
os.system("echo 'NUMBER OF ENTRIES: '")
os.system("clikraken ol | grep {} | wc -l".format(order_type))

