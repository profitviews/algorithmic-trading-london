from profitview import Link, http, logger


class Trading(Link): 
    """
	Send market orders via the BitMEX UI.  This will provoke a call back to:
	- order_update() since an order is entered and filled
	- fill_update() since there's a fill as the trade goes through
	- trade_update() since there's a trade
	"""
    def order_update(self, src, sym, data):
		if sym == 'LTCUSD':
			logger.info(f"ORDER UPDATE\n{src}, {sym}, {data}\n{'-'*100}\n") 

    def fill_update(self, src, sym, data):
		if sym == 'LTCUSD':
			logger.info(f"FILL UPDATE\n{src}, {sym}, {data}\n{'-'*100}\n")

    def trade_update(self, src, sym, data):
		# if sym == 'LTCUSD':
		logger.info(f"TRADE UPDATE\n{src}, {sym}, {data}\n{'-'*100}\n")

			
			
			
