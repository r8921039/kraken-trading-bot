#!/usr/bin/env python3

from lib import *

#
# main
#

### WARNING!!! it fails between 701000 and 702000, likely too big a number
###create_order("sell", 701000, 702000, 100)

#delete_orders("buy")
#add_orders("buy", 5700, 5801, 100)
os.system("clikraken ol | grep buy")
