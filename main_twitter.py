import logging
from time import sleep
from modules.twitter.twitter_bot import BotTwitter

logging.basicConfig(filename="twitter_bot.log", level=logging.DEBUG)

def main():
    twitter = BotTwitter(debug=True)
    twitter.run()

if __name__ == "__main__":
    main()