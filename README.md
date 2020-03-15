
### INTRO
* This trading bot is based on the work [clikraken](https://github.com/zertrin/clikraken.git), 
  which is further based on [python3-krakenex](https://github.com/veox/python3-krakenex)
* Set up 50 2:1 margin buys/longs to help hodlers to provide the BTC market liquidity at time of stress

### STRATEGY
* Simply sets limit buys from USD $5000 all the way down to $100 with fixed $100 a step

### HOWTO
* Follow [clikraken](https://github.com/zertrin/clikraken.git) to set up API keys 
* Copy the provided settings.ini to ~/.config/clikraken/settings.ini 
* Run ./trade.py

### LICENSE
MIT
