import logging

from mustachizer.logging import ConfigureLogger
from mustachizer.twitter.twitter_bot import BotTwitter

# Create logger at the correct level
ConfigureLogger(log_file="twitter_bot", console_level="DEBUG")
logger = logging.getLogger("stachlog")


def main():
    twitter_bot = BotTwitter()
    logger.info("StachBot started")
    try:
        twitter_bot.run()
    except (SystemExit, KeyboardInterrupt):
        pass
    finally:
        logger.info("StachBot stopped")


if __name__ == "__main__":
    main()
