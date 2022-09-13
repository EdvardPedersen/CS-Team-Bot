import math
import discord
import constants


class DiscordString(str):

    def __new__(self, value):
        obj = str.__new__(self, value)
        return obj

    def __add__(self, __s: str) -> str:
        return DiscordString(super().__add__(__s))

    def to_code_block(self, format_type):
        return f"```{format_type}\n{self.__str__()}```\n"

    def to_code_inline(self):
        return f"`{self.__str__()}`"


def member_check(function):
    async def inner(self, message, permissions):
        if permissions < constants.Permissions.member:
            return
        await function(self, message)
    return inner


def admin_check(function):
    async def inner(self, message, permissions):
        if permissions < constants.Permissions.admin:
            return
        await function(self, message)
    return inner


def infinite_sequence_gen():
    num = 0
    while True:
        yield num
        num += 1


def euclidean_distance(val1, val2):
    return math.sqrt((val1-val2)**2)


def list_ranks() -> DiscordString:
    ranks = ""
    for rank, title in constants.ranks.items():
        ranks += f"{rank}:  {title}\n"
    return DiscordString(ranks)


def list_active_duty() -> DiscordString:
    reply = "Active duty maps: | "
    for map in constants.maps:
        reply += f"{map} |"
    reply += "\n"
    return DiscordString(reply)


def log_message(function):
    async def inner(self, message):
        if isinstance(message, discord.RawReactionActionEvent):
            self.log.info(f"{message.user_id} calling: {function.__name__}")
        elif isinstance(message, discord.Message):
            self.log.info(f"{message.author} calling: {function.__name__}")
            self.log.debug(f"Message content: {message.content}")
        await function(self, message)
        self.log.debug("OK")
    return inner
