from modules.twitter.bot import BotTwitter

twitter = BotTwitter(debug=True)
twitter.reply_to_last_mentions()