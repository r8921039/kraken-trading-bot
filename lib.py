#!/usr/bin/env python3

# MEMO
#date -r 1584214882
#date -j -f "%Y %j %H %M %S" "2020 12 15 00 00 00" "+%s"

import copy
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

# key: open order key
# val: open order value
def delete_order(key, val = None):
    try:
        cmd = subprocess.Popen(["clikraken", "--raw", "x", key], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        cmd.wait()
        out, err = cmd.communicate()
        out_json = json.loads(out)
        print(out_json['result'])
        if (val != None):
            print("DELETED ORDER: %s %s %s %s" % (key, val['descr']['type'], val['descr']['price'], Decimal(val['vol']) - Decimal(val['vol_exec'])))
        else:
            print("DELETED ORDER: %s %s %s $s" % (key, "Unknown", "Unknown", "Unknown"))
    except:
        print("\033[91mUnexpected Error!!\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)

def delete_orders(order_type, price = None):
    try:
        cmd = subprocess.Popen(["clikraken", "--raw", "ol"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        cmd.wait()
        out, err = cmd.communicate()
        out_json = json.loads(out)
        ol_k = list(out_json['result']['open'].keys())
        ol_v = list(out_json['result']['open'].values())
        j = 0
        print("DELETE ORDERS:") 
        for i in ol_v:
            if (i['descr']['type'] == order_type):
                if (price == None or Decimal(i['descr']['price']) == Decimal(price)):
                    delete_order(ol_k[j], i)
            j += 1
    except:
        print("\033[91mUnexpected Error!!\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)

#
# order_type: buy/sell
# start_price:
# end_price: 
# step_price:
#
def add_orders(order_type, start_price, step_price, order_count, vol, lev, dry_run = False):
    try:
        print("PLACE ORDER:")
        price = Decimal(start_price)
        for i in range(1, order_count + 1):
            args = ["clikraken", "--raw", "p", "-t", "limit", order_type, str(vol), str(price)]
            if (lev != None and lev != "1:1"):
                args.append("-l")
                args.append(lev)
            if (dry_run == True):
                args.append("-v")
            cmd = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            cmd.wait()
            out, err = cmd.communicate()
            out_json = json.loads(out)
            try:
                print(out_json['result'])
            except:
                print(out_json)
            price += Decimal(step_price)
    except:
        print("\033[91mUnexpected Error!!\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)


def show_balance():
    try: 
        cmd = subprocess.Popen(["clikraken", "--raw", "bal"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        cmd.wait()
        out, err = cmd.communicate()
        out_json = json.loads(out)
        #print(out_json)
        bal_xbt = Decimal(out_json['result']['XXBT'])
        bal_usd = Decimal(out_json['result']['ZUSD'])
        print("\033[96m{:<20s}{:>15s}\033[00m".format("ACCOUNT BALANCE:", "VOL"))
        print("\033[96m{:<20s}{:>15.8f}\033[00m".format("BTC", bal_xbt))
        print("\033[96m{:<20s}{:>15.8f}\033[00m".format("USD", bal_usd))
        #print()
    except:
        print("\033[91mUnexpected Error!!\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)


def show_trade_balance():
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
        try:
            margin_level = out_json['result']['ml']
        except:
            margin_level = "N/A"
        print("\033[35mOPEN TRADE BALANCE:\033[00m")
        print("\033[35m{:<20s}{:>15s}{:>15s}{:>15s}{:>15s}{:>15s}{:>15s}\033[00m".format("TOTAL ASSET (USD)", "", "", "TOTAL COST", "TOTAL MARGIN", "MARGIN LEVEL", "PNL"))
        print("\033[35m{:<20.8f}{:>15s}{:>15s}{:>15.8f}{:>15.8f}{:>15s}{:>15.2f}\033[00m".format(trade_balance, "", "", pos_cost, margin_used, margin_level, pos_pnl))
        #print()
    except:
        print("\033[91mUnexpected Error!!\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)


def get_ticker():
    try:
        cmd = subprocess.Popen(["clikraken", "--raw", "t"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        cmd.wait()
        out, err = cmd.communicate()
        out_json = json.loads(out)
        #print(out_json)
        ticker = dict()
        ticker["price"] = out_json['result']['XXBTZUSD']['c'][0]
        ticker["vol"] = out_json['result']['XXBTZUSD']['c'][1]
        ticker["ave"] = out_json['result']['XXBTZUSD']['p'][1]
        ticker["ask"] = out_json['result']['XXBTZUSD']['a'][0]
        ticker["bid"] = out_json['result']['XXBTZUSD']['b'][0]
        ticker["high"] = out_json['result']['XXBTZUSD']['h'][1]
        ticker["low"] = out_json['result']['XXBTZUSD']['l'][1]
        #print(ticker)
        return ticker
    except:
        print("\033[91mUnexpected Error!!\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)

def show_ticker(ticker):
    try:
        print("\033[96m{:<20s}{:>15s}{:>15s}{:>15s}{:>15s}{:>15s}{:>15s}\033[00m".format("TICKER:", "PRICE", "ASK", "BID", "WEIGHTED AVE", "HIGH", "LOW"))
        print("\033[96m{:<20s}{:>15s}{:>15s}{:>15s}{:>15s}{:>15s}{:>15s}\033[00m".format("", ticker['price'], ticker['ask'], ticker['bid'], ticker['ave'], ticker['high'], ticker['low']))
        print()
    except:
        print("\033[91m\033[91mUnexpected Error!!\033[00m\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)


def show_ticker_and_depth():
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
        print("\033[91mUnexpected Error!!\033[00m")
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
        print("TICKER AND DEPTH")
        print("{:<20s}{:>15.0f}{:>15.0f}".format("ASKS/WALL:", asks_ave, asks_vol))
        print("{:<20s}{:>15.0f}{:>10.0f}{:>10.0f}".format("TICKER/SPREADS:", ticker_p, asks_ave-ticker_p, ticker_p-bids_ave))
        print("{:<20s}{:>15.0f}{:>15.0f}".format("BIDS/WALL:", bids_ave, bids_vol))
        #print()
    except:
        print("\033[91mUnexpected Error!!\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)

#
# open positions
#

def same_pos(pos_v, pos2_v):
    try:
        if (pos_v == None and pos2_v != None):
            return False
        if (pos_v != None and pos2_v == None):
            return False

        if (pos_v == None and pos2_v == None):
            return True

        pos_vol, pos_type = get_pos_vol(pos_v)
        pos2_vol, pos2_type = get_pos_vol(pos2_v)

        if (pos_type == pos2_type and pos_vol == pos2_vol):
            return True
        else:
            print("Warn!! 2 pos NOT the same: " + str(pos_type) + ":" + str(pos_vol) + " v.s. " + str(pos2_type) + ":" + str(pos2_vol))
            return False
    except:
        print("\033[91mUnexpected Error!!\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)

def get_pos():
    try:
        cmd = subprocess.Popen(["clikraken", "--raw", "pos"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        cmd.wait()
        out, err = cmd.communicate()
        out_json = json.loads(out)
        #print(out_json)
        #pos_k = list(out_json['result'].keys())
        pos_v = list(out_json['result'].values())
        return pos_v
    except:
        print("\033[91mUnexpected Error!!\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)

def get_pos_vol(pos_v):
    try:
        pos_vol = Decimal(0)
        pos_type = None
        for i in pos_v:
            if (Decimal(i['margin']) > 0):
                pos_vol += Decimal(i['vol']) - Decimal(i['vol_closed'])
                if (pos_type == None):
                    pos_type = i['type']
                elif (pos_type != i['type']):
                    print("ERROR!! Position type inconsistency detected!! Abort!!")
                    sys.exit()
            else: 
                print("WARN!! Position with 0 margin detected. Assume okay")
                print(i)
        return pos_vol, pos_type
    except:
        print("\033[91mUnexpected Error!!\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)
    

# comment off itemized, use grouped instead 
#def show_pos(pos_v):
#    try:
#        print("OPEN POSITIONS:")
#        print("{:<25s}{:>5s}{:>15s}{:>15s}{:>15s}".format("ORDERID", "TYPE", "COST", "VOL", "PNL"))
#        for i in pos_v:
#            print("{:<25s}{:>5s}{:>15.8f}{:>15.8f}{:>15.2f}".format(i['ordertxid'], i['type'], Decimal(i['cost']), Decimal(i['vol']) - Decimal(i['vol_closed']), Decimal(i['net'])))
#            # beep sound
#            #print("\a")
#    except:
#        print("\033[91mUnexpected Error!!\033[00m")
#        print('-'*60)
#        traceback.print_exc(file=sys.stdout)
#        print('-'*60)

# show grouped/aggregated cost/vol with the same order id and show 
def show_pos(pos_v):
    try:
        pos_copy = copy.deepcopy(pos_v)
        dist = {}
        for v in pos_copy:
            #print("DIST {}".format(dist))
            if (v['ordertxid'] in dist):
                #print("FOUND IN DIST {}".format(v['ordertxid']))
                dist_v = dist[v['ordertxid']]
                dist_v['cost'] = str(Decimal(dist_v['cost']) + Decimal(v['cost']))
                dist_v['vol'] = str(Decimal(dist_v['vol']) + Decimal(v['vol']))
                dist_v['vol_closed'] = str(Decimal(dist_v['vol_closed']) + Decimal(v['vol_closed']))
                dist_v['fee'] = str(Decimal(dist_v['fee']) + Decimal(v['fee']))
                dist_v['value'] = str(Decimal(dist_v['value']) + Decimal(v['value']))
                dist_v['margin'] = str(Decimal(dist_v['margin']) + Decimal(v['margin']))
                dist_v['net'] = str(Decimal(dist_v['net']) + Decimal(v['net']))
                dist[v['ordertxid']] = dist_v
            else:
                #print("NOT FOUND IN DIST {}".format(v['ordertxid']))
                dist[v['ordertxid']] = v
                
        tot = None
        print("\033[36mGROUPED OPEN POSITIONS:\033[00m")
        print("\033[36m{:<20s}{:>15s}{:>15s}{:>15s}{:>15s}{:>15s}{:>15s}\033[00m".format("ORDERID", "TYPE", "AVE PRICE", "TOTAL COST", "TOTAL MARGIN", "TOTAL VOL", "PNL"))
        for v in dist.values():
            print("\033[96m{:<20s}{:>15s}{:>15.8f}{:>15.8f}{:>15.8f}{:>15.8f}{:>15.2f}\033[00m".format(v['ordertxid'], v['type'], Decimal(v['cost']) / (Decimal(v['vol']) - Decimal(v['vol_closed'])), Decimal(v['cost']), Decimal(v['margin']), Decimal(v['vol']) - Decimal(v['vol_closed']), Decimal(v['net'])))
            # beep sound
            #print("\a"
            if (tot is None):
                tot = v
            else:
                tot['cost'] = str(Decimal(tot['cost']) + Decimal(v['cost']))
                tot['vol'] = str(Decimal(tot['vol']) + Decimal(v['vol']))
                tot['vol_closed'] = str(Decimal(tot['vol_closed']) + Decimal(v['vol_closed']))
                tot['fee'] = str(Decimal(tot['fee']) + Decimal(v['fee']))
                tot['value'] = str(Decimal(tot['value']) + Decimal(v['value']))
                tot['margin'] = str(Decimal(tot['margin']) + Decimal(v['margin']))
                tot['net'] = str(Decimal(tot['net']) + Decimal(v['net']))

        if (tot is not None):
            print("\033[36mSUM:\033[00m")
            print("\033[36m{:<20s}{:>5s}{:>15s}{:>15s}{:>15s}{:>15s}{:>15s}\033[00m".format("ORDERID", "TYPE", "AVE PRICE", "TOTAL COST", "TOTAL MARGIN", "TOTAL VOL", "PNL"))
            print("\033[96m{:<20s}{:>5s}{:>15.8f}{:>15.8f}{:>15.8f}{:>15.8f}{:>15.2f}\033[00m".format("", "", Decimal(tot['cost']) / (Decimal(tot['vol']) - Decimal(tot['vol_closed'])), Decimal(tot['cost']), Decimal(tot['margin']), Decimal(tot['vol']) - Decimal(tot['vol_closed']), Decimal(tot['net'])))
        #print()
    except:
        print("\033[91mUnexpected Error!!\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)

#
# open orders
#

def get_open_orders():
    try:
        cmd = subprocess.Popen(["clikraken", "--raw", "ol"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        cmd.wait()
        out, err = cmd.communicate()
        out_json = json.loads(out)
        #print(out_json)
        ol_k = list(out_json['result']['open'].keys())
        ol_v = list(out_json['result']['open'].values())
        return ol_k, ol_v
    except:
        print("\033[91mUnexpected Error!!\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)

def get_next_buy(ol_k, ol_v):
    return get_next_open(ol_k, ol_v, "buy")
def get_next_sell(ol_k, ol_v):
    return get_next_open(ol_k, ol_v, "sell")
def get_next_open(ol_k, ol_v, order_type): 
    try:
        price = None
        order = None
        index = 0
        j = 0
        for i in ol_v:
            if (i['descr']['type'] == "buy" and i['descr']['type'] == order_type):
                if (price == None or price < Decimal(i['descr']['price'])):
                    price = Decimal(i['descr']['price'])
                    order = i
                    index = j
            elif (i['descr']['type'] == "sell" and i['descr']['type'] == order_type):
                if (price == None or price > Decimal(i['descr']['price'])):
                    price = Decimal(i['descr']['price'])
                    order = i
                    index = j
            j += 1
        if (order == None):
            return None, None
        else:
            return ol_k[index], order
    except:
        print("\033[91mUnexpected Error!!\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)

def show_next_buy(order_k, order_v):
    show_next_open(order_k, order_v)
def show_next_sell(order_k, order_v):
    show_next_open(order_k, order_v)
def show_next_open(order_k, order_v):
    try:
        if (order_v != None):
            if (order_v['descr']['type'] == "buy"):
                print("\033[32m")
            else:
                print("\033[31m")
            print("{:<20s}{:>15s}{:>15s}{:>15s}".format("NEXT ORDER " + order_v['descr']['type'].upper() + ":", "PRICE" ,"VOL", "LEV"))
            print("{:<20s}{:>15s}{:>15.8f}{:>15s}".format(order_k, order_v['descr']['price'], Decimal(order_v['vol']) - Decimal(order_v['vol_exec']), order_v['descr']['leverage']))
            print("\033[30m")
        #print()
    except:
        print("\033[91mUnexpected Error!!\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)

        
def get_total_buy(open_orders):
    return get_total_open(open_orders, "buy") 
def get_total_sell(open_orders):
    return get_total_open(open_orders, "sell") 
def get_total_open(open_orders, order_type):
    try:
        vol = Decimal(0)
        for i in open_orders:
            if (i['descr']['type'] == order_type):
                    vol = vol + Decimal(i['vol']) - Decimal(i['vol_exec'])
        return vol
    except:
        print("\033[91mUnexpected Error!!\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)

def show_total_buy(vol):
    show_total_open(vol, "buy")
def show_total_sell(vol):
    show_total_open(vol, "sell")
def show_total_open(vol, order_type):
    try:
        print("\033[33m{:<20s}{:>15s}{:>15s}\033[00m".format("TOTAL " + order_type.upper() + " ORDER:", "", "VOL"))
        if (vol != None):
            print("\033[33m{:<20s}{:>15s}{:>15.8f}\033[00m".format("", "", vol))
        #print()
    except:
        print("\033[91mUnexpected Error!!\033[00m")
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print('-'*60)
