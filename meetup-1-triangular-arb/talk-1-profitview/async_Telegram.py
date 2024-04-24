from profitview import Link, http, logger
from pyrogram import Client
import asyncio
import shelve


class Pr:
    SHELF_NAME = 'Telegram'
	APP_NAME = 'ProfitViewAlerter' 


class Trading(Link):

    def on_start(self):
		self.shelf = shelve.open(Pr.SHELF_NAME)
		
		self.session_string = self.shelf.get('session_string')
		if self.session_string:
			logger.info("Using saved session string")
			self.app = Client(Pr.APP_NAME, session_string=self.session_string)
		else:
			logger.info("Add code to set up session")
			raise RuntimeError("Code not added to setup session")

		self.loop = asyncio.get_event_loop()
	
	@http.route
    def get_connect(self, data):
		self.loop.run_until_complete(self.connect())
		
	async def connect(self):
		logger.info("Connecting to Telegram")
		await self.app.connect()
		
		if not self.session_string:
			logger.info("Requesting code")
			self.sent_code_info = await self.app.send_code(self.phone_number)
			# Note that at this point you will be sent a code via Telegram
			
    @http.route
    def get_code(self, data):
        # If there is no cached session string you use this end-point to provide the Telegram code
		self.code = data['code']
		
	@http.route
	def get_send(self, data):
		self.loop.run_until_complete(self.send(data['who'], data['text']))
		
	async def send(self, who, text):
		logger.info("execute()")
		if not self.session_string:
			logger.info("No session string yet so sign in with Telegram code")
			res = await self.app.sign_in(self.phone_number, self.sent_code_info.phone_code_hash, self.code)

			logger.info("Get and save session string")
			self.session_string = self.shelf['session_string'] = await self.app.export_session_string()

		logger.info(f"Send the message {text} to {who}")
		send_res = await self.app.send_message(who, text)
		logger.info("Message sent")
