import logging
import sys

from mustachizer.discord.discord_bot import DiscordBot

logging.basicConfig(stream=sys.stdout)


def main():
    token = None
    with open("./modules/discord/.token") as token_file:
        token = token_file.read()
    bot = DiscordBot()
    bot.run(token)


if __name__ == "__main__":
    main()
