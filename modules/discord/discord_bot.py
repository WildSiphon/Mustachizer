import io

import discord

from modules.mustache.errors import NoFaceFoundError
from modules.mustache.mustachizer import Mustachizer
from modules.mustache.sentence_provider import SentenceProvider


class DiscordBot(discord.Client):
    def __init__(self, debug=False):
        super().__init__()
        self.__mustachizer = Mustachizer(debug)
        self.__sentence_provider = SentenceProvider()

    async def on_ready(self):
        print("Stachbot ready to mustache !")

    async def on_message(self, message: discord.Message):
        # Avoid recursion
        if message.author != self.user:

            # A user tagged the bot
            if self.user in message.mentions:
                print(message.reference.resolved.embeds[0].url)

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
