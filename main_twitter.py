from time import sleep
from io import BytesIO
from modules.twitter.twitter_bot import BotTwitter

twitter = BotTwitter(debug=True)
# medias = twitter._mustachize_urls(urls=["https://media.giphy.com/media/65ATXZgKw9tKnJua1B/giphy.gif"])
# twitter._reply_with_twitter_api(medias=medias)

# with open("/tmp/face.gif", "wb") as save_file:
#     save_file.write(medias[0].read())

while True:
	twitter.reply_to_last_mentions()
	sleep(10)