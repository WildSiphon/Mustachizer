from mustachizer.discord.discord_bot import DiscordBot
from mustachizer.logging.configuration import ConfigureLogger

# Create logger at the correct level
ConfigureLogger(log_file="discord_bot", console_level="INFO")


def main():
    token = None
    with open("./modules/discord/.token") as token_file:
        token = token_file.read()
    bot = DiscordBot()
    bot.run(token)


if __name__ == "__main__":
    main()
