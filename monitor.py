#!/usr/bin/env python3

from lib import *

#
# main
#

while True:
    if (first_time):
        first_time = False
    else:
        for i in range(1, 60):
            time.sleep(1)
            print(".", end =" ", flush=True)
        print("")
        #os.system('clear')
    print('='*60)
    print("KRAKEN TRADING BOT %s" % datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y"))
    print('='*60)

    #
    # get balance
    #
    get_balance()

    #
    # get ticker and depth
    #
    get_ticker_and_depth()

    #
    # get active/open positions 
    #
    #show_open_positions(get_open_positions())

    #
    # get active/open positions
    #
    get_trade_balance()

    #
    # get open orders 
    #
    get_open_orders()

 
