#!/usr/bin/env python3

import pickle
import datetime
import random
import re
import discord
from pytube import Playlist
'''
Interface:

!register - start registration for next match(this week or next week default to wednesdays)
- The bot gives a message that people react to to register
- Manual stop of registration

- After registration, registered users can PM bot to set map preferences with
!maps
- The bot responds with a list of all maps, with a reaction to each map containing number 1-7
- User reacts with the appropriate rank for the map
- The bot ends with a question of which rank the user is

!teams
- The bot rolls teams for matches
- Teams are assigned a pool of maps they will play based on preferences
- Balanced by rank and map pool
- Ban order is decided
'''


class Configuration():
    def __init__(self,owner=None, admin=[], server=None, role=None):
        self.owner = None
        self.super_users_id = None
        self.server = None
        self.team_role = None
        self.parseParams(owner,admin,server,role)
        self.guild = ""
        self.role = ""
    
    def parseParams(self,owner,admin,server,role):
        self.owner = owner
        self.super_users_id = admin
        self.super_users_id.append(self.owner)
        self.server = server
        self.team_role = role


class Registration():
    def __init__(self,users,date=None) -> None:
        self.date = None
        self.playdate_next(date)
        self.players = users
        self.status = False

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
        self.status = True

    def set_passive(self):
        self.status = False

class RegistrationManager:
    def __init__(self):
        self.registration_active = False
        self.next_match = None
        self.registration_next = None
        self.registration_post = None
        self.my_regex = re.compile("^!registration")

    def method(self, message):
        if my_regex.match(message.content):
            pass

class GenericMessageHandler:
    def __init__(self, command, help_text, response, reply_private=False):
        self.regex = re.compile(f"^{command}$")
        self.response = response
        self.help_text = help_text
        self.private = reply_private

    async def method(self, message, permissions):
        if not self.regex.match(message.content):
            return
        if self.private:
            await message.author.send(self.response)
        else:
            await message.channel.send(self.response)


class CsBot(discord.Client):
    def __init__(self, config):
        intents = discord.Intents.default()
        intents.members = True
        intents.reactions = True
        super().__init__(intents=intents)
        self.config = config
        self.broadcast_channel = None
        self.message_handlers = []
        self.reaction_handlers = []
        self.message_handlers.append(GenericMessageHandler("!signup", "Sign up for season", "Not implemented", False))
        self.message_handlers.append(GenericMessageHandler("!optout", "Opt out of the rest of the season", "Not implemented", True))
        self.message_handlers.append(GenericMessageHandler("!register", "Start registration for match", "Not implemented", True))
        self.message_handlers.append(GenericMessageHandler("!cancel", "Cancel match registration", "Not implemented", True))
        self.message_handlers.append(GenericMessageHandler("!end", "End registration period for next match", "Not implemented", True))
        self.message_handlers.append(GenericMessageHandler("!next", "Show next match", "Not implemented", True))
        self.message_handlers.append(GenericMessageHandler("!upcoming", "???", "Not implemented", True))
        self.message_handlers.append(GenericMessageHandler("!maps", "Start registration of map preferences", "Not implemented", True))
        self.message_handlers.append(GenericMessageHandler("!purge", "???", "Not implemented", True))
        self.message_handlers.append(GenericMessageHandler("!easterEgg", "???", "Not implemented", True))
        self.message_handlers.append(GenericMessageHandler("!dank", "???", "Not implemented", True))
        self.message_handlers.append(GenericMessageHandler("!setAdmin", "???", "Not implemented", True))
        self.message_handlers.append(GenericMessageHandler("!removeAdmin", "???", "Not implemented", True))
        self.message_handlers.append(GenericMessageHandler("!admins", "???", "Not implemented", True))
        self.message_handlers.append(GenericMessageHandler("!shutdown", "???", "Not implemented", True))
        self.message_handlers.append(GenericMessageHandler("!reset", "???", "Not implemented", True))

    async def on_ready(self):
        self.config.role = await self.get_role()
        for channel in self.get_all_channels():
            if channel.name == "general":
                self.broadcast_channel = channel
        
        if not self.broadcast_channel:
            print("Could not set broadcast_channel")

    async def get_role(self):
        for g in self.guilds:
            print(g)
            for r in g.roles:
                print(r)
                if r.id == self.config.team_role:
                    self.config.guild = g
                    print(r)
                    return r

    async def on_raw_reaction_add(self, reaction):
        permissions = await self.get_permissions(message.author)
        for handler in self.reaction_handlers:
            await handler.method(reaction, permissions)

    async def on_raw_reaction_remove(self, reaction):
        permissions = await self.get_permissions(message.author)
        for handler in self.reaction_handlers:
            await handler.method(reaction, permissions)

    async def on_message(self, message):
        if message.author == self.user:
            return
        permissions = await self.get_permissions(message.author)
        for handler in self.message_handlers:
            await handler.method(message, permissions)

    async def get_permissions(self, user):
        if user.id in self.config.super_users_id:
            return 3
        if user in self.config.role.members:
            return 2
        return 1


if __name__ == "__main__":
    token = ""
    try:
        with open("auth") as f:
            token = f.read()
    except FileNotFoundError:
        print("Unable to read authToken")

    admins = []
    try:
        with open("admins") as f:
            for admin in f.readlines():
                admins.append(int(admin))
    except FileNotFoundError:
        print("No admins added, ;only owner has access to core features")


    config = Configuration(188422488080777217, admins, 875657026775158805, 878372503196676106)
    client = CsBot(config)
    client.run(token)
