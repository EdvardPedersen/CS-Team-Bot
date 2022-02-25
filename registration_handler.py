import re
from generic_message_handler import GenericMessageHandler
from constants import Permissions, ranks, maps
from player import Player
from match import MatchDay, test_banorder

def permission_check(function):
    async def inner(self, message, permissions):
        if permissions < Permissions.admin:
            return
        await function(self,message)
    return inner

class RegistrationHandler(GenericMessageHandler):
    def __init__(self,help_text,response,reply_private):
        super().__init__(help_text,response,reply_private)
        self.teammembers = None
        ["open","closed","ready"]
        self.registration_status = "ready"
        self.matchday = None
        self.player_pool = {}

    @permission_check
    async def message_list_players(self, message):
        players = "UiT Players: \n"
        for player in self.player_pool.values():
            players += f"{player.name}: {ranks[player.rank]} maps: `{(sorted(player.maps,key=lambda k:player.maps[k],reverse=True))}`\n"
        await self.reply(message, players)

    @permission_check
    async def message_banorder(self,message):
        if not self.registration_status == "closed":
            await self.reply(message, "No matches found")
            return
        if not self.matchday.banorder_message:
            if not self.matchday.teams:
                await self.reply(message, "Teams not rolled")
                return
            message = await self.reply(message,f"{self.matchday.banorder()}")
            self.matchday.banorder_message = message
        else:
            await self.matchday.message.reply(":arrow_up:")
    
    @permission_check
    async def message_register(self,message):
        if self.registration_status == "open":
            await self.matchday.message.reply("Registration already active")
            return
        elif self.registration_status == "closed":
            await self.matchday.message.reply("Registration already done, please delete the old one before starting a new registration")
            return

        arguments = re.match("^![a-zA-Z]*\s(\d{1,2}$)",message.content)
        if arguments:
            num_matches = int(arguments.group(1))
            if num_matches < 1:
                num_matches = 2
        else:
            num_matches = 2
        self.matchday = MatchDay({},num_matches)
        self.matchday.set_message(await message.channel.send(f"{self.teammembers.mention}React to this post to sign up for the [{self.matchday.num_matches}] matches on: {self.matchday.date}"))
        await self.matchday.message.pin()
        self.registration_status = "open"

    @permission_check
    async def message_cancel(self, message):
        if self.registration_status == "open":
            await self.matchday.message.unpin()
            await self.matchday.message.delete()
            self.matchday = None
            self.registration_status = "ready"
            await self.reply(message,"Cancelled match day registration")
        else:
            await self.reply(message,"No registration active")
    
    @permission_check
    async def message_end(self, message):
        if self.registration_status == "open":
            self.matchday.set_message(await message.channel.fetch_message(self.matchday.message.id))
            for reaction in self.matchday.message.reactions:
                for u in await reaction.users().flatten():
                    self.matchday.players[u.id] = self.player_pool[u.id]
            self.registration_status = "closed"
            await self.matchday.message.unpin()
            await self.reply(message,"Registration ended")
        else:
            await self.reply(message,"No registration active")

    @permission_check
    async def message_next(self,message):
        if self.matchday:
            players = [player.name for player in self.matchday.players.values()]
            await self.reply(message,f"Next match: {self.matchday.date}\nPlaying: {players}")
        else:
            await self.reply(message, "No match found")

    @permission_check
    async def message_delete(self,message):
        if self.registration_status == "closed":
            self.matchday = None
            self.registration_status = "ready"
            await message.author.send("Deleted registration")

    @permission_check
    async def message_teams(self, message):
        if not self.matchday:
            await self.reply(message, "No matches found")
            return

        self.matchday.setup_teams()
        teamlist = self.matchday.get_teamlist()
        await self.reply(message, teamlist)

    @permission_check
    async def reaction_add(self,reaction):
        if self.matchday.message and self.matchday.message.id == reaction.message_id:
            if not reaction.user_id in self.player_pool:
                self.player_pool[reaction.user_id] = Player(reaction.user_id,reaction.member.name)
                await reaction.member.send("Please register your rank with '!rank' and map-preferences with '!maps'")

    def _list_ranks(self):
        ranklist = ""
        for rank, title in ranks.items():
            ranklist += f"{rank}: {title}\n"
        return ranklist

    @permission_check
    async def message_list_ranks(self, message):
        await self.reply(message, self._list_ranks())

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
        if self.registration_status == "ready":
            return
        
        maps = message.content.split(' ')[1:]
        await self.matchday.ban(maps)

    @permission_check
    async def message_unban(self,message):
        if self.registration_status == "ready":
            return
        
        maps = message.content.split(' ')[1:]
        self.matchday.unban(maps)

    @permission_check
    async def message_test_banorder(self,message):
        print(test_banorder())