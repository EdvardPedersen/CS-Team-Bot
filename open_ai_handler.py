import io
import logging
import aiohttp
import openai
import discord
from generic_message_handler import GenericMessageHandler
from helper_functions import member_check, log_message


class GTPHandler(GenericMessageHandler):
    """
    Template for handlers
    Methods that handle messages should be named message_<command>
    Methods that handle reactions should be named reaction_<event>
    """

    def __init__(self, help_text, response, reply_private, log_level=logging.WARNING):
        super().__init__(help_text, response, reply_private, log_level)
        self.log.debug("TemplateHandler initialized")
        openai.api_key = self.read_key(".openai")
        openai.organization = "org-iFQwpj4qVGO4dpjjmZ7A1BRv"
        self.complete_model = "text-davinci-003"
        self.chat_model = "gpt-3.5-turbo"

    def read_key(self, filename=".openai"):
        with open(f"{filename}", "r") as f:
            return f.read()

    @member_check
    @log_message
    async def message_complete(self, message):
        self.log.debug("Complete message received")
        reply = ""
        content = message.content.removeprefix("!complete ")
        c = openai.Completion.create(
            model=self.complete_model,
            prompt=f"{content}",
            max_tokens=100,
            top_p=0.3,
        )
        for choice in c.choices:
            if len(reply) + len(choice.text) > 2000:
                await message.channel.send(reply)
                reply = ""
            reply += choice.text + "\n"
        await message.channel.send(reply)

    @member_check
    @log_message
    async def message_chat(self, message):
        content = message.content.removeprefix("!chat ")
        reply = ""
        c = openai.ChatCompletion.create(
            model=self.chat_model, messages=[{"role": "user", "content": content}]
        )

        for choice in c.choices:
            if len(reply) + len(choice.message.content) > 2000:
                await message.channel.send(reply)
                reply = ""
            reply += choice.message.content + "\n"
        await message.channel.send(reply)

    @member_check
    @log_message
    async def message_image(self, message):
        content = message.content.removeprefix("!image ")
        images = openai.Image.create(prompt=f"{content}", n=1, size="512x512")
        # Can this be done in a better way?
        for link in [link.url for link in images.data]:
            async with aiohttp.ClientSession() as session:
                async with session.get(link) as resp:
                    img = await resp.read()
                    with io.BytesIO(img) as file:
                        await message.channel.send(file=discord.File(file, "image.png"))
