import tweepy
import json
import requests
import numpy
import os
from time import sleep

class BotTwitter:

	def __init__(self,debug=False):
		self.debug = debug
		self.tmp = './img/tmp/'

		try:
			self._connect()
			self.name = self.api.me().name
			self.screen_name = self.api.me().screen_name
			self.id = self.api.me().id_str
			if debug: print(f"Connected to \'{self.name}\' @{self.screen_name}")
		except Exception as e:
			print(e)

	def _get_credentials(self):
		with open('./modules/twitter/credentials.json','r') as f:
			token = json.load(f)
		self.consumer_key = token['API_KEY']
		self.consumer_secret = token['API_SECRET_KEY']
		self.access_token = token['ACCESS_TOKEN']
		self.access_token_secret = token['ACCESS_TOKEN_SECRET']

	def _connect(self):
		self._get_credentials()
		auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
		auth.secure = True
		auth.set_access_token(self.access_token, self.access_token_secret)
		self.api = tweepy.API(auth)

	def _empty_tmp(self):
		for filename in os.listdir(self.tmp): os.remove(f"{self.tmp}{filename}")

	def _download_media(self,url,name='tmp'):
		with open(f"{self.tmp}{name}.jpg", 'wb') as handle:
			response = requests.get(url, stream=True)
			if not response.ok: return
			for block in response.iter_content(1024):
				if not block: break
				handle.write(block)

	def _mustachize(self,urls):
		count=0
		for url in urls:
			print(url)
			self._download_media(url,f"{count}")
			count+=1

	def _get_last_mentions(self,max_tweets=1000):
		searched_tweets = [status._json for status in tweepy.Cursor(self.api.search, q=f"@{self.screen_name}").items(max_tweets)]
		self.last_mentions = [tweet for tweet in searched_tweets if self.screen_name in [t['screen_name'] for t in tweet['entities']['user_mentions']]]

	def _reply_with_media(self,in_reply_to_status_id='',status='testytest'):
		media_ids = [self.api.media_upload(f"{self.tmp}{filename}").media_id_string for filename in os.listdir(self.tmp)]
		self.api.update_status(status=status,media_ids=media_ids,in_reply_to_status_id=in_reply_to_status_id,auto_populate_reply_metadata=True)

	def reply_to_last_mentions(self):
		self._get_last_mentions()
		for tweet in self.last_mentions:
			if 'media' in tweet['entities']:
				print("MEDIA",end=' ')
				urls = [media['media_url_https'] for media in tweet['extended_entities']['media']]
				print(f"MUUUUUUUUSTACHE THESE MOTHERFUCKER : {urls}")
				self._mustachize(urls)
				self._reply_with_media(tweet['id_str'])
				self._empty_tmp()
			elif tweet['in_reply_to_status_id_str']:		
				print("REPLY")
			else:
				print("Not a response and no media added to the tweet")