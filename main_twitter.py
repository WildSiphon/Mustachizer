from time import sleep
from modules.twitter.bot import BotTwitter

twitter = BotTwitter(debug=True)
while True:
	twitter.reply_to_last_mentions()
	sleep(10)