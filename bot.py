#!/usr/bin/env python3

import pickle
import datetime
import random
import re
import discord
from pytube import Playlist
from generic_message_handler import GenericMessageHandler
from configuration import Configuration
from match_handler import Registration, RegistrationManager
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
