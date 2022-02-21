import re
from generic_message_handler import GenericMessageHandler
from constants import Permissions, ranks, maps
from player import Player
from match import MatchDay


class RegistrationHandler(GenericMessageHandler):
    def __init__(self,help_text,response,reply_private):
        super().__init__(help_text,response,reply_private)
        ["open","closed","ready"]
        self.registration_status = "ready"
        self.match_message = None
        self.matchday = None
        self.player_pool = {}

    async def message_list_players(self, message, permission):
        if permission < Permissions.admin:
            return
        players = "UiT Players: \n"
        for player in self.player_pool.values():
            players += f"{player.name}: {ranks[player.rank]} maps: `{(sorted(player.maps,key=lambda k:player.maps[k],reverse=True))}`\n"
        await self.reply(message, players)

    async def message_banorder(self,message,permission):
        if permission < Permissions.admin:
            return
        await self.reply(message,f"{self.matchday.banorder()}")

    async def message_register(self,message,permission):
        if permission < Permissions.admin:
            return
        if self.registration_status == "open":
            await self.match_message.reply("Registration already active")
            return
        elif self.registration_status == "closed":
            await self.match_message.reply("Registration already done, please delete the old one before starting a new registration")
            return

        arguments = re.match("^![a-zA-Z]*\s(\d{1,2}$)",message.content)
        if arguments:
            num_matches = int(arguments.group(1))
            if num_matches < 1:
                num_matches = 2
        else:
            num_matches = 2
        self.matchday = MatchDay({},num_matches)

        self.match_message = await message.channel.send(f"React to this post to sign up for the [{self.matchday.num_matches}] matches on: {self.matchday.date}")
        self.registration_status = "open"

    async def message_cancel(self, message,permission):
        if permission < Permissions.admin:
            return
        if self.registration_status == "open":
            self.matchday = None
            self.registration_status = "ready"
            await self.match_message.delete()
            self.match_message = None
            await self.reply("Cancelled match day registration")
        else:
            await self.reply(message,"No registration active")
    
    async def message_end(self, message,permission):
        if permission < Permissions.admin:
            return
        if self.registration_status == "open":
            self.match_message = await message.channel.fetch_message(self.match_message.id)
            for reaction in self.match_message.reactions:
                for u in await reaction.users().flatten():
                    self.matchday.players[u.id] = self.player_pool[u.id]
            self.registration_status = "closed"
            await self.reply(message,"Registration ended")
        else:
            await self.reply(message,"No registration active")

    async def message_next(self,message,permission):
        if permission < Permissions.admin:
            return
        if self.matchday:
            players = [player.name for player in self.matchday.players.values()]
            await self.reply(message,f"Next match: {self.matchday.date}\nPlaying: {players}")
        else:
            await self.reply(message, "No match found")

    async def message_delete(self,message,permission):
        if permission < Permissions.admin:
            return
        if self.registration_status == "closed":
            date = self.matchday.date
            day = self.matchday.playday
            self.matchday = None
            self.registration_status = "ready"
            await self.reply(message, f"Registration for matchday on {day}: {date} removed")

    async def message_teams(self, message, permission):
        if permission < Permissions.admin:
            return

        if not self.matchday:
            await self.reply(message, "No matches found")
            return

        self.matchday.setup_teams()
        teamlist = self.matchday.get_teamlist()
        await self.reply(message, teamlist)

    async def reaction_add(self,reaction,permission):
        if permission < Permissions.admin:
            return
        if self.match_message and self.match_message.id == reaction.message_id:
            if not reaction.user_id in self.player_pool:
                self.player_pool[reaction.user_id] = Player(reaction.user_id,reaction.member.name)
                await reaction.member.send("Please register your rank with '!rank' and map-preferences with '!maps'")

    def list_ranks(self):
        ranklist = ""
        for rank, title in ranks.items():
            ranklist += f"{rank}: {title}\n"
        return ranklist

    async def message_list_ranks(self, message, permission):
        if permission < Permissions.admin:
            return
        await self.reply(message, self.list_ranks())

    async def message_rank(self, message, permission):
        if permission < Permissions.admin:
            return
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

    async def message_map_info_player(self,message,permission):
        if not message.author.id in self.player_pool:
            return
        player = self.player_pool[message.author.id]
        await self.reply(message, player.map_ranking())

    def list_maps(self) -> str:
        mapslist = ""
        for map in maps:
            mapslist += f"{map} "
        return mapslist

    async def message_maps(self, message, permission):
        if permission < Permissions.admin:
            return
        if message.author.id not in self.player_pool:
            player = Player(message.author.id,message.author.name)
            self.player_pool[player.id] = player
        res = message.content.split(' ')[1:]
        if len(res) != 7:
            await self.reply(message,f"Please give map preference as a space-separated list from most wanted to least wanted map like:\n`!maps {self.list_maps()}`")
            return
        player = self.player_pool[message.author.id]
        try:
            for i in range(len(maps)):
                player.maps[res[i]] = len(maps) - i
        except Exception as e:
            print(e)
            await message.author.send("Invalid map name")
        await self.reply(message, "Maps registered")

            

