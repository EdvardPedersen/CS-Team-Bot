import re
import constants
from generic_message_handler import GenericMessageHandler
from helper_functions import member_check
from player import Player
from match import MatchDay
from tests import test_banorder

class RegistrationHandler(GenericMessageHandler):
    def __init__(self,help_text,response,reply_private, permission_req):
        super().__init__(help_text,response,reply_private)
        self.broadcast_channel = None
        self.teammembers = None
        self.matchday = MatchDay({})
        self.player_pool = {}
        self.permission_req = permission_req

    @member_check
    async def message_list_players(self, message):
        players_message = f"UiT Players: \n"
        for player in self.player_pool.values():
            players_message += f"`{player.get_info()}`\n"
        await self.reply(message, players_message)

    @member_check
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

    @member_check
    async def message_register(self,message):
        try:
            self.matchday.message = await self.reply(message, self.matchday.registration_start(message.content))
        except AttributeError as err:
            await self.matchday.reply(f'Registration is already {err}\n')
        except NameError:
            await self.reply(message, "Registration in invalid state\n")

    @member_check
    async def message_cancel(self, message):
        await self.reply(message, await self.matchday.registration_cancel())
    
    @member_check
    async def message_end(self, message):
        await self.matchday.refetch_message()
        await self.reply(message,await self.matchday.registration_end(self.player_pool))

    @member_check
    async def message_next(self,message):
        await self.reply(message, self.matchday.next_match())

    @member_check
    async def message_delete(self,message):
        await self.matchday.delete()

    @member_check
    async def message_teams(self, message):
        if not self.matchday:
            await self.reply(message, "No matches found")
        else:
            await self.reply(message, self.matchday.get_teamlist())

    @member_check
    async def reaction_add(self,reaction):
        if self.matchday.message and self.matchday.message.id == reaction.message_id:
            if not reaction.user_id in self.player_pool:
                self.player_pool[reaction.user_id] = Player(reaction.user_id,reaction.member.name)
                await reaction.member.send("Please register your rank with '!rank' and map-preferences with '!maps'")

    @member_check
    async def message_list_ranks(self, message):
        ranks =  ""
        for rank, title in ranks.items():
            ranks += f"{rank}:  {title}\n"
        await self.reply(message, ranks)

    @member_check
    async def message_list_maps(self, message):
        reply =  "Active duty maps: | "
        for map in constants.maps:
            reply  += f"{map} |"
        reply += "\n"
        self.reply(message, reply)

    def list_ranks(self):
        r = ""
        for rank, title in  constants.ranks.items():
            r += f"{rank}: {title}\n"
        return  r

    @member_check
    async def message_rank(self, message):
        res = re.match("^![a-zA-Z]+\s(\d{1,})",message.content)
        if not res:
            await message.author.send("Please set rank with '!rank ' followed by rank number")
            await message.author.send(f"Ranks:\n{self.list_ranks()}")
            return

        rank = int(res.group(1))
        if not rank:
            await message.author.send("Please set rank with '!rank ' followed by a rank number")
            return
        if rank >18 or rank <1:
            await message.author.send("Invalid rank")
            return
        if not message.author.id in self.player_pool:
            player = Player(message.author.id,message.author.name)
            player.set_rank(rank)
            self.player_pool[player.id] = player
        else:
            player = self.player_pool[message.author.id]
            player.set_rank(rank)
        await message.author.send(f"Your registered rank:{player.rank}")

    @member_check
    async def message_player_map_info(self,message):
        if not message.author.id in self.player_pool:
            return

        args = re.match("^![a-zA-Z_]*\s([a-zA-Z\d]*)$",message.content)
        if args:
            name = args.group(1)
            for id,p in  self.player_pool.items():
                if name == p.name:
                    player = self.player_pool[id]
                    break
        else:
            player = self.player_pool[message.author.id]
        await self.reply(message, player.get_map_ranking())

    @member_check
    async def message_player_info(self,message):
        IDarg = re.match("^![a-zA-Z_]*\s*([\d]+)$",message.content)
        NameArg = re.match("^![a-zA-Z_]+\s+([a-zA-Z\d]+)$",message.content)
        if IDarg:
            id = int(IDarg.group(1))
            try:
                p = self.player_pool[id]
                await self.reply(message,p.get_info())
            except KeyError:
                await self.reply(message,"Player not found")
        elif NameArg:
            name = NameArg.group(1)
            for id,player in  self.player_pool.items():
                if name == player.name:
                    await self.reply(message,player.get_info())
                    break
        else:
            try:
                p = self.player_pool[message.author.id]
                await self.reply(message,p.get_info())
            except KeyError:
                await self.reply(message, "Please register")

    def _list_maps(self) -> str:
        mapslist = ""
        for map in constants.maps:
            mapslist += f"{map} "
        return mapslist

    @member_check
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
            for i in range(len(constants.maps)):
                if not res[i] in constants.maps:
                    raise KeyError(f"{res[i]}")
                tmpmap[res[i]] = len(constants.maps) - i
            for map in constants.maps:
                if map not in tmpmap.keys():
                    tmpmap[map] = 0
            player.maps = tmpmap
            await self.reply(message, "Maps registered")
        except Exception as e:
            await message.author.send(f"Invalid map name {e}")

    @member_check
    async def message_ban(self,message):
        maps = message.content.split(' ')[1:]
        for map in maps:
            await self.matchday.ban(map)

    @member_check
    async def message_unban(self,message):
        maps = message.content.split(' ')[1:]
        for map in maps:
            await self.matchday.unban(map)

    @member_check
    async def message_pick(self, message):
        maps = message.content.split(' ')[1:]
        for map in maps:
            await self.matchday.pick(map)
    
    @member_check
    async def message_unpick(self, message):
        maps = message.content.split(' ')[1:]
        for map in maps:
            await self.matchday.unpick(map)