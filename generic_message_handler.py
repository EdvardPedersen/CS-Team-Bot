import re

class GenericMessageHandler:
    def __init__(self, command, help_text, response, reply_private=False):
        self.regex = re.compile(f"^{command}$")
        self.response = response
        self.help_text = help_text
        self.private = reply_private

    async def method(self, message, permissions):
        if not self.regex.match(message.content):
            return
        if self.private:
            await message.author.send(self.response)
        else:
            await message.channel.send(self.response)
