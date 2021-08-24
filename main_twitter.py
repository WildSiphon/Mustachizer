from time import sleep
from modules.twitter.twitter_bot import BotTwitter

def main():
    twitter = BotTwitter(debug=True)
    while True:
      twitter.reply_to_last_mentions()

if __name__ == "__main__":
    main()