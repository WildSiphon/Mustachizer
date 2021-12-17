from mustachizer.logging.configuration import ConfigureLogger
from mustachizer.twitter.twitter_bot import BotTwitter

# Create logger at the correct level
ConfigureLogger(log_file="twitter_bot", console_level="INFO")


def main():
    twitter = BotTwitter(debug=False)
    twitter.run()


if __name__ == "__main__":
    main()
