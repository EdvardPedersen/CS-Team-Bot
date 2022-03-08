import re
from generic_message_handler import GenericMessageHandler
from constants import Permissions, ranks, maps
from player import Player
from match import MatchDay
from tests import test_banorder

def permission_check(function):
    async def inner(self, message, permissions):
        if permissions < Permissions.admin:
            return
        await function(self,message)
    return inner

class RegistrationHandler(GenericMessageHandler):
    def __init__(self,help_text,response,reply_private):
        super().__init__(help_text,response,reply_private)
        self.broadcast_channel = None
        self.teammembers = None
        self.matchday = MatchDay({})
        self.player_pool = {}

    @permission_check
    async def message_list_players(self, message):
        players_message = "UiT Players: \n"
        for player in self.player_pool.values():
            players_message += player.get_info()
        await self.reply(message, players_message)

    @permission_check
    async def message_banorder(self,message):
        if self.matchday.veto == "active":
            await self.matchday.message.reply(":arrow_up:")
        else:
            try:
                m = await self.reply(message, self.matchday.banorder())
                self.matchday.set_banorder_message(m)
                self.matchday.veto = "active"
            except AttributeError as err:
                await self.reply(message, f"Matchday registration status: {err}")
            except NameError:
                await self.reply(message, f"Matchday  is in invalid state")
    
    @permission_check
    async def message_register(self,message):
        try:
            self.matchday.message = await self.reply(message, self.matchday.registration_start(message.content))
        except AttributeError as err:
            await self.matchday.reply(f'Registration is already {err}\n')
        except NameError:
            await self.reply(message, "Registration in invalid state\n")

    @permission_check
    async def message_cancel(self, message):
        await self.reply(message, await self.matchday.registration_cancel())
    
    @permission_check
    async def message_end(self, message):
        await self.reply(message,await self.matchday.registration_end(self.player_pool))

    @permission_check
    async def message_next(self,message):
        await self.reply(message, self.matchday.next_match())

    @permission_check
    async def message_delete(self,message):
        await self.matchday.delete()

    @permission_check
    async def message_teams(self, message):
        if not self.matchday:
            await self.reply(message, "No matches found")
            return
        await self.reply(message, self.matchday.get_teamlist())

    @permission_check
    async def reaction_add(self,reaction):
        if self.matchday.message and self.matchday.message.id == reaction.message_id:
            if not reaction.user_id in self.player_pool:
                self.player_pool[reaction.user_id] = Player(reaction.user_id,reaction.member.name)
                await reaction.member.send("Please register your rank with '!rank' and map-preferences with '!maps'")

    @permission_check
    async def message_list_ranks(self, message):
        ranks =  ""
        for rank, title in ranks.items():
            ranks += f"{rank}:  {title}\n"
        await self.reply(message, ranks)

    @permission_check
    async def message_list_maps(self, message):
        reply =  "Active duty maps: | "
        for map in maps:
            reply  += f"{map} |"
        reply += "\n"
        self.reply(message, reply)

    def list_ranks(self):
        r = ""
        for rank, title in  ranks.items():
            r += f"{rank}: {title}\n"
        return  r

    @permission_check
    async def message_rank(self, message):
        res = re.match("^![a-zA-Z]*\s(\d{1,})",message.content)
        if not res:
            await message.author.send("Please set rank with '!rank ' followed by rank number")
            await message.author.send(f"Ranks:\n{self.list_ranks()}")
            return
        rank = int(res.group(1))

        if not rank:
            await message.author.send("Please set rank with '!rank ' followed by a rank number")
            return
        if rank >18 or rank <1:
            await message.author.send("Please set rank with '!rank ' followed by a rank number")
            return
        if not message.author.id in self.player_pool:
            player = Player(message.author.id,message.author.name)
            player.set_rank(rank)
            self.player_pool[player.id] = player
        else:
            player = self.player_pool[message.author.id]
            player.set_rank(rank)
        await message.author.send(f"Your registered rank:{ranks[rank]}")

    @permission_check
    async def message_map_info_player(self,message):
        if not message.author.id in self.player_pool:
            return
        player = self.player_pool[message.author.id]
        await self.reply(message, player.map_ranking())

    def _list_maps(self) -> str:
        mapslist = ""
        for map in maps:
            mapslist += f"{map} "
        return mapslist

    @permission_check
    async def message_maps(self, message):
        if message.author.id not in self.player_pool:
            player = Player(message.author.id,message.author.name)
            self.player_pool[player.id] = player
        res = message.content.split(' ')[1:]
        if len(res) != 7:
            await self.reply(message,f"Please give map preference as a space-separated list from most wanted to least wanted map like:\n`!maps {self._list_maps()}`")
            return
        player = self.player_pool[message.author.id]
        try:
            tmpmap = {}
            for i in range(len(maps)):
                if not res[i] in maps:
                    raise KeyError(f"{res[i]}")
                tmpmap[res[i]] = len(maps) - i
            player.maps = tmpmap
            await self.reply(message, "Maps registered")
        except Exception as e:
            print(e)
            await message.author.send(f"Invalid map name {e}")

    @permission_check
    async def message_ban(self,message):
        maps = message.content.split(' ')[1:]
        for map in maps:
            await self.matchday.ban(map)

    @permission_check
    async def message_unban(self,message):
        maps = message.content.split(' ')[1:]
        for map in maps:
            self.matchday.unban(map)

    @permission_check
    async def message_test_banorder(self,message):
        await self.reply(message,await test_banorder())