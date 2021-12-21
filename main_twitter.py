import logging

from mustachizer.logging.configuration import ConfigureLogger
from mustachizer.twitter.twitter_bot import BotTwitter

# Create logger at the correct level
ConfigureLogger(log_file="twitter_bot", console_level="DEBUG")
logger = logging.getLogger("stachlog")


def main():
    twitter_bot = BotTwitter()
    logger.info("+======== BOT STARTED ========+")
    try:
        twitter_bot.run()
    except (SystemExit, KeyboardInterrupt) as error:
        logger.error(error)
    finally:
        logger.info("+======== BOT STOPPED ========+")


if __name__ == "__main__":
    main()
