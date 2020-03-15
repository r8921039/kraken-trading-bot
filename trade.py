#!/usr/bin/env python3

# MEMO
#date -r 1584214882
#date -j -f "%Y %j %H %M %S" "2013 2 12 34 56" "+%a %b %d %T %Z %Y"

import datetime
from decimal import Decimal 
import json
import time
import traceback
import subprocess
import sys

first_time = True

#
# func
#

def delete_order(order_type):
    cmd = subprocess.Popen(["clikraken", "--raw", "ol"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    cmd.wait()
    out, err = cmd.communicate()
    out_json = json.loads(out)
    ol_k = list(out_json['result']['open'].keys())
    ol_v = list(out_json['result']['open'].values())
    j = 0
    for i in ol_v:
        if (i['descr']['type'] == order_type):
            print("DELETE ORDER: %s %s %s %s" % (ol_k[j], i['descr']['type'], i['descr']['price'], i['vol']))
            cmd = subprocess.Popen(["clikraken", "--raw", "x", ol_k[j]], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            cmd.wait()
            out, err = cmd.communicate()
            out_json = json.loads(out)
            print(out_json['result'])
        j += 1

def create_order(order_type, start_price, end_price, step_price):
    print("CREATE ORDER:")
    for price in range(start_price, end_price, step_price):
        cmd = subprocess.Popen(["clikraken", "--raw", "p", "-l", "2:1", "-t", "limit", order_type, "1", str(price)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        cmd.wait()
        out, err = cmd.communicate()
        out_json = json.loads(out)
        print(out_json['result'])

#
# delete/create order 
#

#delete_order("sell")
#delete_order("buy")

### WARNING!!! it fails between 701000 and 702000, likely too big a number
###create_order("sell", 701000, 702000, 100)

#create_order("sell", 19000, 20100, 100)
#create_order("buy", 100, 5100, 100)

#sys.exit()

#
# main loop
#

while True:
    print('='*60)
    if (first_time):
        first_time = False
    else:
        time.sleep(60)
    print(datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y"))

    #
    # get balance
    #
    try: 
        cmd = subprocess.Popen(["clikraken", "--raw", "bal"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        cmd.wait()
        out, err = cmd.communicate()
        out_json = json.loads(out)
        #print(out_json)
        bal_xbt = Decimal(out_json['result']['XXBT'])
        bal_usd = Decimal(out_json['result']['ZUSD'])
    except:
        print("Unexpected Error!!")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)
        continue

    #
    # get depth
    #
    try:
        cmd = subprocess.Popen(["clikraken", "--raw", "d", "-c", "100"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        cmd.wait()
        out, err = cmd.communicate()
        out_json = json.loads(out)
        #print(out_json)

        asks = out_json['result']['XXBTZUSD']['asks']
        asks_ave = Decimal(0)
        asks_vol = Decimal(0)
        for i in asks:
            asks_ave += Decimal(i[0]) * Decimal(i[1])
            asks_vol += Decimal(i[1])
        asks_ave /= asks_vol

        bids = out_json['result']['XXBTZUSD']['bids']
        bids_ave = Decimal(0) 
        bids_vol = Decimal(0)
        for i in bids:
            bids_ave += Decimal(i[0]) * Decimal(i[1])
            bids_vol += Decimal(i[1])
        bids_ave /= bids_vol
    except:
        print("Unexpected Error!!")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)
        continue

    #
    # get ticker 
    #
    try:
        cmd = subprocess.Popen(["clikraken", "--raw", "t"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        cmd.wait()
        out, err = cmd.communicate()
        out_json = json.loads(out)
        #print(out_json)
        ticker_p = Decimal(out_json['result']['XXBTZUSD']['c'][0])
        ticker_v = Decimal(out_json['result']['XXBTZUSD']['c'][1])
        print("{:<20s}{:>20.0f}{:>20.0f}".format("ASKS/WALL:", asks_ave, asks_vol))
        print("{:<20s}{:>20.0f}{:>10.0f}{:>10.0f}".format("TICKER/SPREADS:", ticker_p, asks_ave-ticker_p, ticker_p-bids_ave))
        print("{:<20s}{:>20.0f}{:>20.0f}".format("BIDS/WALL:", bids_ave, bids_vol))
    except:
        print("Unexpected Error!!")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)
        continue

    #
    # get active/open positions 
    #
    try:
        cmd = subprocess.Popen(["clikraken", "--raw", "pos"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        cmd.wait()
        out, err = cmd.communicate()
        out_json = json.loads(out)
        print("ACTIVE/OPEN POSITIONS:")
        #print(out_json)
        pos = list(out_json['result'])
        for i in pos:
            print("{:>20s}{:>10.0s}{:>10.0f}{:>10.0f}{:>10.0f}".format(pos['ordertxid'], pos['type'], Decimal(pos['cost']), Decimal(pos['vol']), Decimal(pos['net'])))
    except:
        print("Unexpected Error!!")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)
        continue

    #
    # get open orders 
    #
    try:
        cmd = subprocess.Popen(["clikraken", "--raw", "ol"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        cmd.wait()
        out, err = cmd.communicate()
        out_json = json.loads(out)
        #print(out_json)
        ol_k = list(out_json['result']['open'].keys())
        ol_v = list(out_json['result']['open'].values())
        ol_sell_p = None
        ol_sell_v = None
        ol_sell_l = None
        ol_buy_p = None
        ol_buy_v = None
        ol_buy_l = None
        #j = 0
        for i in ol_v:
            if (i['descr']['type'] == "sell"):
                if (ol_sell_p == None or ol_sell_p > Decimal(i['descr']['price'])):
                    ol_sell_p = Decimal(i['descr']['price'])
                    ol_sell_v = Decimal(i['vol'])
                    ol_sell_l = i['descr']['leverage']
            elif (i['descr']['type'] == "buy"):
                if (ol_buy_p == None or ol_buy_p < Decimal(i['descr']['price'])):
                    ol_buy_p = Decimal(i['descr']['price'])
                    ol_buy_v = Decimal(i['vol'])
                    ol_buy_l = i['descr']['leverage']
            #print(ol_k[j])
            #j += 1

        if (ol_sell_p != None):
            print("{:<20s}{:>20.0f}{:>10.0f}{:>10.0s}".format("NEXT SELL/VOL/1-5X:", ol_sell_p, ol_sell_v, ol_sell_l))
        else:
            print("{:<20s}{:>20s}".format("NEXT SELL/VOL/1-5X:", "None"))

        if (ol_buy_p != None):
            print("{:<20s}{:>20.0f}{:>10.0f}{:>10.0s}".format("NEXT BUY/VOL/1-5X:", ol_buy_p, ol_buy_v, ol_buy_l))
        else:
            print("{:<20s}{:>20s}".format("NEXT BUY/VOL/1-5X:", "None"))

    except:
        print("Unexpected Error!!")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)
        continue

print("program exit!")
        
