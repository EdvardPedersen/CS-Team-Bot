import datetime
import inspect
import re
from generic_message_handler import GenericMessageHandler
from registration_handler import RegistrationHandler
from helper_functions import DiscordString, admin_check, log_message, member_check


class AdminHandler(GenericMessageHandler):
    def __init__(self, bot, help_text, response, reply_private, log_level):
        super().__init__(help_text, response, reply_private, log_level)
        self.bot = bot

    def _get_message_handler(self, type):
        handler = None
        for h in self.bot.message_handlers:
            if isinstance(h, type):
                handler = h
                break

        return handler

    def _get_reaction_handler(self, type):
        handler = None
        for h in self.bot.reaction_handlers:
            if isinstance(h, type):
                handler = h
                break

        return handler

    @admin_check
    @log_message
    async def message_playday(self, message):
        args = re.match(r"^![a-zA-Z]+\s([a-zA-Z]+)$", message.content)
        reg_handler = self._get_message_handler(RegistrationHandler)
        if not args:
            return
        else:
            day = args.group(1)
            if day not in reg_handler.matchday.weekdays:
                self.log.debug(f"Invalid playday:{day}")
                await self.reply(message, f"Invalid weekday: {day}")
                return
            reg_handler.matchday.playday = day
            await self.reply(message, f"Playday set to: {day}")

    @admin_check
    @log_message
    async def message_playtime(self, message):
        args = re.match(r"^![a-zA-Z]+\s(\d{2}):(\d{2})", message.content)
        handler = self._get_message_handler(RegistrationHandler)
        if not args:
            return
        else:
            hour = int(args.group(1))
            if hour > 24 or hour < 0:
                await self.reply(message, "Invalid hour. Expect:<hour[2]:minute[2]>")
                return
            minute = int(args.group(2))
            if minute > 59 or minute < 0:
                await self.reply(message, "Invalid minute. Expect:<hour[2]:mintute[2]>")
                return

            handler.matchday.playtime = datetime.time(hour=hour, minute=minute)
            await self.reply(message, f"New playtime: {handler.matchday.playtime}")

    @member_check
    @log_message
    async def message_commands(self, message):
        commands = []
        for handler in self.bot.message_handlers:
            if isinstance(handler, AdminHandler):
                continue
            for name, _ in inspect.getmembers(handler, predicate=inspect.ismethod):
                if name.startswith("message_"):
                    commands.append(f"{name.removeprefix('message_')}\n")
        commands = sorted(commands)
        reply = ""
        for c in commands:
            reply += c
        await self.reply(message, DiscordString(reply).to_code_block(""))
