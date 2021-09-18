from time import sleep
from modules.twitter.twitter_bot import BotTwitter

def main():
    twitter = BotTwitter(debug=True)
    twitter.run()

if __name__ == "__main__":
    main()