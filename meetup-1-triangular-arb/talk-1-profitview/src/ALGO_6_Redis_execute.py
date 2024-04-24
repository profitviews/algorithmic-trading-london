from profitview import Link, logger


class Strategy: 
    VENUE = 'WooPaper'
    SIZE = 0.0001  # BTC
	SYM = 1
	SIDE = 0

    
class Trading(Link):
    def on_start(self):
		""" Setup signal connection"""
		self.redis.subscribe({'intent': self.trade})
		
	def trade(self, data):
		# logger.info(data)
		self.create_market_order(
			Strategy.VENUE, data[Strategy.SYM], data[Strategy.SIDE], Strategy.SIZE)
