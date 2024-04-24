from profitview import Link, logger
import talib
import numpy as np 


class Strategy:
    VENUE = 'WooPaper'
    REVERSION = .1
    LOOKBACK = 5
    SIZE = 0.0001  # BTC 

    
class Trading(Link):
    def on_start(self):
        self.prices = np.array([], dtype=float)
		self.elements = 0
		self.mean = 0
		logger.info(f"{Strategy.VENUE} {Strategy.REVERSION} {Strategy.LOOKBACK} {Strategy.SIZE}")

    def trade_update(self, src, sym, data):
		newPrice = float(data["price"])
        self.prices = np.append(self.prices, newPrice)
		logger.info(f"{src} {sym} {newPrice=}")
        if len(self.prices) <= Strategy.LOOKBACK:
            # Until we have enough data for the mean
            self.mean = np.mean(self.prices)
        else:  # Move and recalculate mean
            self.prices = self.prices[1:]
            self.mean = np.mean(self.prices)
			stddev = talib.STDDEV(self.prices, timeperiod=Strategy.LOOKBACK)[-1] 
			logger.info(f"\n{stddev=}\n")
            stdReversion = Strategy.REVERSION*stddev
			logger.info(f"checking for extreme")
            if newPrice > self.mean + stdReversion:  # Upper extreme - Sell!
				logger.info("Time to sell")
                self.create_market_order(Strategy.VENUE, sym, "Sell", Strategy.SIZE)
            if newPrice < self.mean - stdReversion:  # Lower extreme - Buy!
				logger.info("Time to buy")
                self.create_market_order(Strategy.VENUE, sym, "Buy", Strategy.SIZE)