from profitview import Link, http, logger
import time


class Trading(Link): 
    def quote_update(self, src, sym, data):
		latency = self.epoch_now - data['time'] 
		logger.info(f"{latency =:>5.0f} ms")
