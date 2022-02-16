import inspect
import re
import datetime
import discord
from generic_message_handler import GenericMessageHandler
from constants import Permissions, ranks, maps
from player import Player
from team_roll import roll_teams

class Match():
    def __init__(self,users,num_matches=2,date=None) -> None:
        self.date = None
        self.playdate_next(date)
        self.players = users
        self.status = "active"
        self.teams = None
        self.num_matches = num_matches

    def playdate_next(self,date):
        if date:
            self.date = date
        else:
            playday = "Wednesday"
            weekdays = {
                'Monday':0,
                'Tuesday':1,
                'Wednesday':2,
                'Thursday':3,
                'Friday':4,
                'Saturday':5,
                'Sunday':6,
            }
            days_in_week = len(weekdays.keys())
            today = datetime.date.today()
            days_to = weekdays[playday] - datetime.date.weekday(today)
            if days_to < 0: # we are past playday this week
                days_to += days_in_week
            self.date =  today + datetime.timedelta(days_to)

    def set_active(self):
        self.status = "active"

    def set_passive(self):
        self.status = "inactive"
    
    def team_setup(self):
        if not self.teams:
            self.teams = roll_teams(self.players,self.num_matches)
        
class RegistrationHandler(GenericMessageHandler):
    def __init__(self,help_text,response,reply_private):
        super().__init__(help_text,response,reply_private)
        self.registration_active = False
        self.registration_next = None
        self.registration_post = None
        self.match_post = None
        self.match_next = None
        self.player_pool = {}

    async def message_list_players(self, message, permission):
        if permission < Permissions.admin:
            return
        players = "UiT Players: \n"
        for player in self.player_pool.values():
            players += f"{player.name}: {ranks[player.rank]} maps: `{[x for x in reversed(sorted(player.maps,key=lambda k:player.maps[k]))]}`\n"
        await self.reply(message, players)

    async def message_register(self,message,permission):
        if permission < Permissions.admin:
            return
        if self.registration_active:
            self.reply(message, "Registration already active")
            return
        res = re.match("^![a-zA-Z]*\s(\d{1})",message.content)
        if res:
            num_matches = int(res.group(1))
            if num_matches < 1:
                await self.reply(message, "Registration only allowed for 1 or more matches")
                return
            self.registration_next = Match({},num_matches)
        else:
            self.registration_next = Match({})
        if self.match_next and self.match_next.date == self.registration_next.date:
            self.registration_next = None
            await self.reply(message,f"Match registration for {self.match_next.date} already done, please delete previous registration first")
            return
        self.registration_post = await message.channel.send(f"React to this post to sign up for the next matchday on: {self.registration_next.date}")
        self.registration_active = True
        # await self.reply(message,"Registration not implemented")

    async def message_cancel(self, message,permission):
        if permission < Permissions.admin:
            return
        if self.registration_active:
            self.registration_next = None
            self.registration_active = None
            await self.registration_post.delete()
            await message.author.send("Cancelled match day registration")
        else:
            await self.reply(message,"No registration active")
        # await self.reply(message,"Cancelation not implements")
    
    async def message_end(self, message,permission):
        if permission < Permissions.admin:
            return
        if self.registration_next:
            self.match_next = self.registration_next
            self.match_post = self.registration_post

            self.registration_post = None
            self.registration_next = None
            self.registration_active = False
            await self.reply(message,"Registration ended")
        else:
            await self.reply(message,"No registration active")
        # await self.reply(message,"End not implemented")

    async def message_next(self,message,permission):
        if permission < Permissions.admin:
            return
        if self.match_next:
            # move to match object
            players = [player.name for player in self.match_next.players.values()]
            await self.reply(message,f"Next match: {self.match_next.date}\nPlaying: {players}")
        else:
            await self.reply(message, "No match found")

    async def message_delete(self,message,permission):
        if permission < Permissions.admin:
            return
        if self.match_next:
            date = self.match_next.date
            self.match_next = None
            await self.match_post.delete()
            await self.reply(message, f"Registration for match on: {date} removed")

    async def message_teams(self, message, permission):
        if permission < Permissions.admin:
            return

        if not self.match_next:
            await self.reply(message, "No match found")
            return

        self.match_next.team_setup()
        teams = ""
        i = 1
        for team in self.match_next.teams: 
            teams += f"Team {i}:{[player.name for player in team]}\n"
            i += 1
        await self.reply(message, teams)

    async def reaction_add(self,reaction,permission):
        if permission < Permissions.admin:
            return
        if self.registration_post and self.registration_post.id == reaction.message_id:
            if reaction.member.id in self.registration_next.players:
                return
            else:
                if not reaction.member.id in self.player_pool:
                    self.player_pool[reaction.member.id] = Player(reaction.member.id,reaction.member.name)
                    await reaction.member.send("Please answer me with *'!rank <your rank[0-17]>'* Where 0->Silver 1, 17->Global Elite")
                player = self.player_pool[reaction.member.id]
                self.registration_next.players[player.id]= player
                await reaction.member.send(f"You are now signed up for the match on {self.registration_next.date}")

    async def reaction_remove(self, reaction, permission):
        if permission < Permissions.admin:
            return
        if self.registration_post and self.registration_post.id == reaction.message_id:
            if reaction.user_id in self.registration_next.players:
                del self.registration_next.players[reaction.user_id]
                await reaction.member.send(f"You have been removed from the match on {self.registration_next.date}")

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


    def list_maps(self):
        mapranking = ""
        for map in maps:
            mapranking += f"{map} "
        return mapranking

    async def message_map_info_player(self,message,permission):
        if not message.author.id in self.player_pool:
            return
        player = self.player_pool[message.author.id]
        await self.reply(message, player.map_ranking())

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

            

