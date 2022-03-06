import math


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