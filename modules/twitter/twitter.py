import tweepy,json

def connect():
	global api
	with open('./modules/twitter/credentials.json','r') as f:
		token = json.load(f)

	consumer_key = token['API_KEY']
	consumer_secret = token['API_SECRET_KEY']
	access_token = token['ACCESS_TOKEN']
	access_token_secret = token['ACCESS_TOKEN_SECRET']
	
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.secure = True
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth)

def postMedia(filename,status):
	try:
		api.update_with_media(filename, status)
	except Exception as e:
		print(e)
		return -1