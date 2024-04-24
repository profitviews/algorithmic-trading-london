from profitview import Link, http, logger, cron
import time, datetime
import redis 

cron.options['auto_start'] = False


class Trading(Link):
    """See docs: https://profitview.net/docs/trading/"""

    def on_start(self):
		# Establish connection to external Redis
		self.redis_client = redis.from_url(
			"redis://:yOurReDIzPASwOrd@redis-12345.c6.eu-west-1-1.ec2.cloud.redislabs.com:12345")
		
		# Subscribe to our Redis
		self.redis.subscribe({'control': self.controller})

		self.trade_count = 0
		self.start_time = self.epoch_now  # Milliseconds
		
		cron.start(run_now=True)
		
    def trade_update(self, src, sym, data):
		# Count trades so far
		self.trade_count += 1
		
	@cron.run(every=5)
	def cron_test(self):
		start_time = datetime.datetime.fromtimestamp(self.start_time/1000).strftime('%c')
		message = f"There were {self.trade_count} trades since {start_time}"
		logger.info(message)
		self.redis_client.publish('trade_report', message)
		
	def controller(self, data):
		if data[0] == 'reset':
			logger.info("Received reset")
			self.trade_count = 0
			self.start_time = self.epoch_now
