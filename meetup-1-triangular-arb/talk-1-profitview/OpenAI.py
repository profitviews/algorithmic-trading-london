from profitview import Link, http, logger
import openai
from openai import OpenAI
import os
import shelve
import requests
import json
import asyncio
import datetime


class Pr:
	MODEL = "gpt-4"
	GPT_API_KEY = "sk-your-api-key" 
	TEMPERATURE = 0.6
	MAX_TOKENS = 10
	PRICING_URL = lambda coin: f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
	SHELF_NAME = "AIBlog"
	BASE_TEXT = lambda coin, price, today: f"""
	Create a Twitter post predicting the likely trajectory of cryptocurrency 
	{coin} for 2024 such that it at least includes the aspects of {coin}
	that are unique or unusual in the analysis.  It should use {price} as
	its base price as of {today}.  Include both high and low price targets.
	Add reasonable hashtags.  Put it in a form ready to paste into Twitter
	"""
	

class Trading(Link):
    def on_start(self):
		os.environ["OPENAI_API_KEY"] = Pr.GPT_API_KEY
		self.client = OpenAI()
		self.shelf = shelve.open(Pr.SHELF_NAME)
		self.coin = None
		self.loop = asyncio.get_event_loop()

	def price_coin(self):
		logger.info(f"{self.coin=}")
		"""Check whether there is price info on the coin passed and return it if so"""
		coin = self.coin.lower()
		url = Pr.PRICING_URL(coin)
		logger.info(f"{url=}")
		if response := requests.get(url):
			logger.info(f"{response=} {response.content=}")
			data = response.json()
			logger.info(f"{data=}")
			return data[coin]["usd"] if data and data[coin] else None
		else: return None

	@http.route
    def get_initiate(self, data):
		logger.info(f"Data: {data}")
		self.coin = data['Coin']
		today = datetime.datetime.now().strftime("%B %d, %Y")
		if price := self.price_coin():
			content = Pr.BASE_TEXT(self.coin, price, today)
			self.loop.run_until_complete(self.initiate(data, content))
			return True
		return False
	
	async def initiate(self, data, content):
		logger.info(f"Coin: {self.coin}")
		response = self.client.chat.completions.create(
			model=Pr.MODEL,
			response_format={ "type": "text"},
			messages = [{"role": "user", "content": content}],
			temperature=Pr.TEMPERATURE, max_tokens=Pr.MAX_TOKENS,
			frequency_penalty=0.0)
		logger.info(f"{response=}")
		tweet_content = response.choices[0].message.content
		logger.info(f"{tweet_content=}")
		logger.info(f"{self.coin=}")
		tweet = json.dumps([[self.coin.capitalize(),blog_content]])
		self.shelf[self.coin] = tweet

	@http.route
    def post_predict(self, data):
		if tweet := self.shelf.get(data['Coin']):
	        return json.loads(tweet)
		return json.loads(json.dumps([[self.coin.capitalize(), "No coin price found"]]))
