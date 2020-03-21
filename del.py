#!/usr/bin/env python3

from lib import *

if (len(sys.argv) == 2):
    order_type = sys.argv[1]
    if (order_type == "sell" or order_type == "buy"):
        delete_orders(order_type)
        os.system("echo 'NUMBER OF OPEN ENTRIES FOR THE ORDER TYPE: '")
        os.system("clikraken ol | grep {} | wc -l".format(order_type))
    else:
        print("ERROR! please specify sell or buy")
        sys.exit()
else: 
    print("ERROR! please specify sell or buy")
    sys.exit()
