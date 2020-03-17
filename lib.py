#!/usr/bin/env python3

# MEMO
#date -r 1584214882
#date -j -f "%Y %j %H %M %S" "2013 2 12 34 56" "+%a %b %d %T %Z %Y"

import datetime
from decimal import Decimal 
import json
import os
import subprocess
import sys
import time
import traceback

os.system('clear')
first_time = True

#
# order_type: buy/sell
#
def delete_orders(order_type):
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


#
# order_type: buy/sell
# start_price:
# end_price: 
# step_price:
#
def add_orders(order_type, start_price, step_price, order_count, order_size, dry_run = False):
    print("PLACE ORDER:")
    price = Decimal(start_price)
    for i in range(1, order_count + 1):
        # for dry run, add "-v" before "-t"i
        args = ["clikraken", "--raw", "p", "-l", "5:1", "-t", "limit", order_type, str(order_size), str(price)]
        if (dry_run == True):
            args.append("-v")
        cmd = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        cmd.wait()
        out, err = cmd.communicate()
        out_json = json.loads(out)
        print(out_json['result'])
        price += Decimal(step_price)


def get_balance():
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


def get_trade_balance():
    try: 
        cmd = subprocess.Popen(["clikraken", "--raw", "tbal"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        cmd.wait()
        out, err = cmd.communicate()
        out_json = json.loads(out)
        #print(out_json)
        trade_balance = Decimal(out_json['result']['tb'])
        margin_used = Decimal(out_json['result']['m'])
        pos_cost = Decimal(out_json['result']['c'])
        pos_pnl = Decimal(out_json['result']['n'])
        margin_level = Decimal(out_json['result']['ml'])
        print("TRADE BALANCE:")
        print("{:<25s}{:>5s}{:>20s}{:>20s}{:>20s}{:>20s}{:>10s}".format("BALANCE", "", "", "COST", "MARGIN", "MARGIN LEVEL", "PNL"))
        print("{:<25.8f}{:>5s}{:>20s}{:>20.8f}{:>20.8f}{:>20.2f}{:>10.2f}".format(trade_balance, "", "", pos_cost, margin_used, margin_level, pos_pnl))
    except:
        print("Unexpected Error!!")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)


def get_ticker_and_depth():
    # depth
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

    # ticker
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


def get_open_positions():
    try:
        cmd = subprocess.Popen(["clikraken", "--raw", "pos"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        cmd.wait()
        out, err = cmd.communicate()
        out_json = json.loads(out)
        #print(out_json)
        pos_k = list(out_json['result'].keys())
        pos_v = list(out_json['result'].values())
        return pos_k, pos_v
    except:
        print("Unexpected Error!!")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)

##
## show itemized active/open trade entries
##
## pos_k: list of keys (not used)
## pos_v: list of values
#def show_open_positions(pos_k, pos_v):
#    try:
#        print("OPEN POSITIONS:")
#        print("{:<25s}{:>5s}{:>20s}{:>20s}{:>20s}".format("ORDERID", "TYPE", "COST", "VOL", "PNL"))
#        for i in pos_v:
#            print("{:<25s}{:>5s}{:>20.8f}{:>20.8f}{:>20.2f}".format(i['ordertxid'], i['type'], Decimal(i['cost']), Decimal(i['vol']) - Decimal(v['vol_closed']), Decimal(i['net'])))
#            # beep sound
#            #print("\a")
#    except:
#        print("Unexpected Error!!")
#        print('-'*60)
#        traceback.print_exc(file=sys.stdout)
#        print('-'*60)

#
# aggregate (group) cost/vol with the same order id and show 
#
# pos_k: list of keys (not used)
# pos_v: list of values 
#
def show_open_positions(pos_k, pos_v):
    try:
        dist = {}
        for v in pos_v:
            #print("DIST {}".format(dist))
            if (v['ordertxid'] in dist):
                #print("FOUND IN DIST {}".format(v['ordertxid']))
                dist_v = dist[v['ordertxid']]
                dist_v['cost'] = Decimal(dist_v['cost']) + Decimal(v['cost'])
                dist_v['vol'] = Decimal(dist_v['vol']) + Decimal(v['vol'])
                dist_v['vol_closed'] = Decimal(dist_v['vol_closed']) + Decimal(v['vol_closed'])
                dist_v['fee'] = Decimal(dist_v['fee']) + Decimal(v['fee'])
                dist_v['value'] = Decimal(dist_v['value']) + Decimal(v['value'])
                dist_v['margin'] = Decimal(dist_v['margin']) + Decimal(v['margin'])
                dist_v['net'] = Decimal(dist_v['net']) + Decimal(v['net'])
                dist[v['ordertxid']] = dist_v
            else:
                #print("NOT FOUND IN DIST {}".format(v['ordertxid']))
                dist[v['ordertxid']] = v
                
        tot = None
        print("GROUPED OPEN POSITIONS:")
        print("{:<25s}{:>5s}{:>20s}{:>20s}{:>20s}{:>20s}{:>10s}".format("ORDERID", "TYPE", "AVE PRICE", "TOTAL COST", "TOTAL MARGIN", "TOTAL VOL", "PNL"))
        for v in dist.values():
            print("{:<25s}{:>5s}{:>20.8f}{:>20.8f}{:>20.8f}{:>20.8f}{:>10.2f}".format(v['ordertxid'], v['type'], Decimal(v['cost']) / (Decimal(v['vol']) - Decimal(v['vol_closed'])), Decimal(v['cost']), Decimal(v['margin']), Decimal(v['vol']) - Decimal(v['vol_closed']), Decimal(v['net'])))
            # beep sound
            #print("\a"
            if (tot is None):
                tot = v
            else:
                tot['cost'] = Decimal(tot['cost']) + Decimal(v['cost'])
                tot['vol'] = Decimal(tot['vol']) + Decimal(v['vol'])
                tot['vol_closed'] = Decimal(tot['vol_closed']) + Decimal(v['vol_closed'])
                tot['fee'] = Decimal(tot['fee']) + Decimal(v['fee'])
                tot['value'] = Decimal(tot['value']) + Decimal(v['value'])
                tot['margin'] = Decimal(tot['margin']) + Decimal(v['margin'])
                tot['net'] = Decimal(tot['net']) + Decimal(v['net'])

        print("SUM:")
        print("{:<25s}{:>5s}{:>20s}{:>20s}{:>20s}{:>20s}{:>10s}".format("ORDERID", "TYPE", "AVE PRICE", "TOTAL COST", "TOTAL MARGIN", "TOTAL VOL", "PNL"))
        print("{:<25s}{:>5s}{:>20.8f}{:>20.8f}{:>20.8f}{:>20.8f}{:>10.2f}".format("", "", Decimal(tot['cost']) / (Decimal(tot['vol']) - Decimal(tot['vol_closed'])), Decimal(tot['cost']), Decimal(tot['margin']), Decimal(tot['vol']) - Decimal(tot['vol_closed']), Decimal(tot['net'])))
    except:
        print("Unexpected Error!!")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)


def get_open_orders():
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

        
