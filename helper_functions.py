import math
import constants


def member_check(function):
    async def inner(self, message, permissions):
        if permissions < constants.Permissions.member:
            return
        await function(self,message)
    return inner

def admin_check(function):
    async def inner(self,message,permissions):
        if permissions<constants.Permissions.admin:
            return
        await function(self,message)
    return inner

def infinite_sequence_gen(self):
    num = 0
    while True:
        yield num
        num += 1

def euclidean_distance(val1, val2):
    return math.sqrt((val1-val2)**2)


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