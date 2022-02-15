import inspect
import re
import datetime
import discord
from generic_message_handler import GenericMessageHandler
from constants import Permissions
from player import Player
from team_roll import roll_teams

class Match():
    def __init__(self,users,date=None) -> None:
        self.date = None
        self.playdate_next(date)
        self.players = users
        self.status = "active"
        self.teams = None

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
            if days_to <= 0: # we are past playday this week
                days_to += days_in_week
            self.date =  today + datetime.timedelta(days_to)

    def set_active(self):
        self.status = "active"

    def set_passive(self):
        self.status = "inactive"
    
    def team_setup(self):
        if not self.teams:
            self.teams = roll_teams(self.players,2)
        
class RegistrationHandler(GenericMessageHandler):
    def __init__(self,help_text,response,reply_private):
        super().__init__(help_text,response,reply_private)
        self.registration_active = False
        self.registration_next = None
        self.registration_post = None
        self.match_post = None
        self.match_next = None

    def set_handler(self,handler):
        self.handler = handler

    async def message_register(self,message,permission):
        if permission < Permissions.admin:
            return
        if self.registration_active:
            self.reply(message, "Registration already active")

        self.registration_next = Match({})
        if self.match_next and self.match_next.date == self.registration_next.date:
            self.registration_next = None
            await self.reply(message,f"Match registration for {self.match_next.date} already done, please delete previous registration first")
            return
        self.registration_post = await message.channel.send(f"React to this post to sign up for the next match on: {self.registration_next.date}")
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
            await message.author.send("No registration active")
        # await self.reply(message,"End not implemented")

    async def message_next(self,message,permission):
        if permission < Permissions.admin:
            return
        if self.match_next:
            # move to match object
            players = [player.name for player in self.match_next.players.values()]
            await self.reply(message,f"Next match: {self.match_next.date}\nPlaying: {players}")

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
        await self.reply(message, f"Team 1:{self.match_next.teams[0]}\nTeam 2:{self.match_next.teams[1]}")

    async def reaction_add(self,reaction,permission):
        if permission < Permissions.admin:
            return
        if self.registration_post and self.registration_post.id == reaction.message_id:
            if reaction.member.id in self.registration_next.players:
                return
            else:
                player = Player(reaction.member.id,reaction.member.name)
                self.registration_next.players[player.id]= player
                await reaction.member.send(f"You are now signed up for the match on {self.registration_next.date}")
        
    async def reaction_remove(self, reaction, permission):
        if permission < Permissions.admin:
            return
        if self.registration_post and self.registration_post.id == reaction.message_id:
            if reaction.user_id in self.registration_next.players:
                del self.registration_next.players[reaction.user_id]
                await reaction.member.send(f"You have been removed from the match on {self.registration_next.date}")
