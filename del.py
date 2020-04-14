#!/usr/bin/env python3

import argparse
from lib import *

sell = False
buy = False
price = None
parser = argparse.ArgumentParser(description='delete args: <sell>/<buy>/<price>')
parser.add_argument('-s', default=sell, action='store_true', help='sell flag (default: %s)' % sell)
parser.add_argument('-b', default=buy, action='store_true', help='buy flag (default: %s)' % buy)
parser.add_argument('-p', default=price, type=int, help='price (default: %s)' % price)
args = parser.parse_args()
sell = args.s
buy = args.b
price = args.p
#print(sell)
#print(buy)
#print(price)
#sys.exit()

if ((sell == False and buy == False) or (sell == True and buy == True)):
    print("ERROR! please specify sell or buy")
    sys.exit()
else:
    if (sell == True):
        order_type = "sell"
    else:
        order_type = "buy"
    delete_orders(order_type, price)
    os.system("echo 'NUMBER OF OPEN ENTRIES FOR THE ORDER TYPE: '")
    os.system("clikraken ol | grep {} | wc -l".format(order_type))
