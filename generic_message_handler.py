import re
import inspect
import discord
from constants import Permissions

class GenericMessageHandler:
    def __init__(self, help_text, response,reply_private):   
        self.command_prefix = '!'
        self.message_prefix = "message_"
        self.reaction_prefix = "reaction_"
        self.response = response
        self.help_text = help_text
        self.private = reply_private
        self.handlers = {}
        self.handler = None

    async def unhandled(self,message):
        await self.reply(message, "Unimplemented")

    async def reply(self, input, response):
        if self.private:
            await input.author.send(response)
        else:
            await input.channel.send(response)

    async def reaction_add(self,event,permission):
        await event.member.send(f"Cool emoji: {event.emoji}")

    async def reaction_remove(self,event,permission):
        await event.member.send(f"Oh noe! {event.emoji} was so cool")

    async def dispatch(self, message, permission):
        # Please, god, refactor me
        if isinstance(message, discord.Message):
            result = re.match("^!([a-zZ-a]*)", message.content)
            if result:
                group = result.group(1)
                for name,method in inspect.getmembers(self, predicate=inspect.ismethod):
                    if name == self.message_prefix+group:
                        await method(message,permission)
        if isinstance(message, discord.RawReactionActionEvent):
            match message.event_type:
                case 'REACTION_ADD':
                    for name,method in inspect.getmembers(self,predicate=inspect.ismethod):
                        if name == self.reaction_prefix+"add":
                            await method(message,permission)
                case "REACTION_REMOVE":
                    for name,method in inspect.getmembers(self,predicate=inspect.ismethod):
                        if name == self.reaction_prefix+"add":
                            await method(message,permission)