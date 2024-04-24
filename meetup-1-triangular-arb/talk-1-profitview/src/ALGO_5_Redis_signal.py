from profitview import Link, logger
import talib
import numpy as np 


class Strategy:
    VENUE = 'WooPaper'
    REVERSION = .1
    LOOKBACK = 5 

    
class Trading(Link):
    def on_start(self):
        self.prices = np.array([], dtype=float)
		self.elements = 0
		self.mean = 0
		
	def signal(self, direction, sym, price):
		logger.info(f"Publishing {sym} at {price}")
		self.redis.publish('intent', [direction, sym, price])

    def trade_update(self, src, sym, data):
		newPrice = float(data["price"])
        self.prices = np.append(self.prices, newPrice)
		logger.info(f"{sym=} {newPrice=}")
        if len(self.prices) <= Strategy.LOOKBACK:
            # Until we have enough data for the mean
            self.mean = np.mean(self.prices)
        else:  # Move and recalculate mean
            self.prices = self.prices[1:]
            self.mean = np.mean(self.prices)
			stddev = talib.STDDEV(self.prices, timeperiod=Strategy.LOOKBACK)[-1] 
			logger.info(f"\n\n {newPrice=} {self.mean=} {stddev=}\n")
            stdReversion = Strategy.REVERSION*stddev
			logger.info(f"checking for extreme")
            if newPrice > self.mean + stdReversion:  # Upper extreme - Sell!
				logger.info("Time to sell")
                self.signal("Sell", sym, newPrice)
            if newPrice < self.mean - stdReversion:  # Lower extreme - Buy!
				logger.info("Time to buy")
                self.signal("Buy", sym, newPrice)