import io
import logging

import discord

from mustachizer.errors import NoFaceFoundError
from mustachizer.mustachizer import Mustachizer
from mustachizer.utilities.sentence_provider import SentenceProvider


class DiscordBot(discord.Client):
    """
    The Discord Bot.
    """

    def __init__(self, debug: bool = False):
        """
        Construct discord's StacheBot.

        :param debug: Whether it should print stuffs, defaults to False
        """
        super().__init__()
        self.__mustachizer = Mustachizer(debug)
        self.__sentence_provider = SentenceProvider()

    async def on_ready(self):
        logging.info("Stachbot ready to mustache !")

    async def on_message(self, message: discord.Message):
        # Avoid recursion
        if message.author != self.user:

            # A user tagged the bot
            if self.user in message.mentions:
                logging.info(message.reference.resolved.embeds[0].url)

                mustachized_images = []

                # The message contains a media
                if message.attachments:
                    mustachized_images.extend(
                        await self.mustachize_attachments(message)
                    )

                # The message is in response of a message containing a media
                elif message.reference:
                    original_message = message.reference.resolved
                    if isinstance(original_message, discord.Message):
                        mustachized_images.extend(
                            await self.mustachize_attachments(original_message)
                        )

                if len(mustachized_images) > 0:
                    await message.channel.send(
                        self.__sentence_provider.provide(),
                        files=mustachized_images,
                        reference=message,
                    )
                else:
                    await message.channel.send("No image or no face found.")

    async def mustachize_attachments(self, message: discord.Message):
        mustachized_images = []
        for attachment in message.attachments:
            if attachment.content_type.startswith("image/"):
                buffer = io.BytesIO()
                await attachment.save(buffer)
                try:
                    mustachized_image = self.__mustachizer.mustachize(buffer)
                    mustachized_images.append(
                        discord.File(
                            mustachized_image,
                            filename=attachment.filename,
                        )
                    )
                except NoFaceFoundError:
                    pass
        return mustachized_images
