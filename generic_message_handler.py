import re
from constants import Permissions
import inspect

class GenericMessageHandler:
    def __init__(self, commands, help_text, response,reply_private,permissionLevel): 
        self.regex = [re.compile(f"^{command}*") for command in commands]
        self.response = response
        self.help_text = help_text
        self.private = reply_private
        self.permissionRequired = permissionLevel
        self.handlers = {}
        self.handler = None
        self.setup_handlers()

    def setup_handlers(self):
        handled = False
        for regex in self.regex:
            for member in inspect.getmembers(self, predicate=inspect.ismethod):
                if regex.match(f"!{member[0]}"):
                    self.handlers[regex] = member[1]
                    handled = True
            if not handled:
                self.handlers[regex] = self.unhandled
            handled = False

    async def unhandled(self,message):
        self.reply(message, self.response)

    async def reply(self, input, response):
        if self.private:
            await input.author.send(response)
        else:
            await input.channel.send(response)

    def match_regex(self,content):
        for regex in self.regex:
            if regex.match(content):
                self.handler = self.handlers[regex]
                return True
        return False

    def set_regex_handler(self, regex, handler):
        self.handlers[regex] = handler

    async def method(self, message, permission):
        if not self.match_regex(message.content):
            return
        if permission < self.permissionRequired:
            return

        await self.reply(message,self.response)
