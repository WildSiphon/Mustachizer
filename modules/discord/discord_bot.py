import io

import discord
from PIL import Image

from modules.mustache.mustachizer import Mustachizer


class DiscordBot(discord.Client):

    def __init__(self):
        super().__init__()
        self.__mustachizer = Mustachizer()

    async def on_ready(self):
        print("Stachbot ready to mustache !")

    async def on_message(self, message: discord.Message):
        # Avoid recursion
        if message.author != self.user:
            if self.user in message.mentions and message.attachments:
                mustachized_images = []
                for attachment in message.attachments:
                    print(attachment.content_type)
                    if attachment.content_type.startswith("image/"):
                        print("Found image !")
                        buffer = io.BytesIO()
                        await attachment.save(buffer)
                        format_ = attachment.content_type.split("/")[-1]
                        mustachized_images.append(discord.File(self.__mustachizer.mustachize(buffer, format_), filename=attachment.filename))
                await message.channel.send("Better like that ;)", files = mustachized_images)
