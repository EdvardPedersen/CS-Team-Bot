import logging
import discord
from generic_message_handler import GenericMessageHandler
from helper_functions import admin_check


def log(function):
    async def inner(self,message):
        if isinstance(message, discord.RawReactionActionEvent):
            self.log.info(f"{message.user_id} calling: {function.__name__}")
        elif isinstance(message, discord.Message):
            self.log.info(f"{message.author} calling: {function.__name__}")
            self.log.debug(f"Message content: {message.content}")
        await function(self,message)
        self.log.debug(f"OK")
    return inner

class AdminHandler(GenericMessageHandler):
    def __init__(self, bot, help_text, response, reply_private):
        super().__init__(help_text, response, reply_private)
        self.bot = bot
        self.log = logging.getLogger(self.__class__.__name__)

    @admin_check
    @log
    async def message_set_log_level(self,message):
        level = message.content.removeprefix("!set_log_level ")
        match level:
            case "debug":
                self.bot.log.setLevel(logging.DEBUG)
            case "info":
                self.bot.log.setLevel(logging.INFO)
            case "warning":
                self.bot.log.setLevel(logging.WARNING)
            case "error":
                self.bot.log.setLevel(logging.ERROR)
            case "critical":
                self.bot.log.setLevel(logging.CRITICAL)
            case _:
                self.reply(message,"Invalid argument")