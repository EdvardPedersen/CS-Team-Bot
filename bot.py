#!/usr/bin/env python3.10

import os
import logging
import discord
from generic_message_handler import GenericMessageHandler
from configuration import Configuration
from registration_handler import RegistrationHandler
from constants import Permissions
from stupid import StupidityHandler
from test_handler import TestHandler

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
        self.log = None
        self.message_handlers = []
        self.reaction_handlers = []

    def handler_setup(self):
        self.log.info("Setting up handlers..")
        self.message_handlers.append(
            GenericMessageHandler("???", "Not implemented", True))
        self.log.debug("genericMessageHandler... OK")
        registrationhandler = RegistrationHandler(
            "server_players.db", "Register new match", "Not implemented", False)
        registrationhandler.teammembers = self.config.role
        registrationhandler.broadcast_channel = self.broadcast_channel
        self.message_handlers.append(registrationhandler)
        self.reaction_handlers.append(registrationhandler)
        self.log.debug("registrationHandler... OK")
        self.message_handlers.append(StupidityHandler(
            "Dad Jokes and Dank memes", "Dad jokes and memes", False))
        self.log.debug("stupidityHandler... OK")
        testHandler = TestHandler("Public tests", "Not implemented", True)
        self.message_handlers.append(testHandler)
        self.reaction_handlers.append(testHandler)
        self.log.debug("testHandler... OK")
        self.log.info("OK")

    def log_setup(self):
        log_format = "%(levelname)s %(name)s %(asctime)s - %(message)s"
        logging.basicConfig(filename=f"{self.__class__.__name__}.log",
                    filemode="a",
                    format=log_format,
                    level=logging.INFO)
        self.log = logging.getLogger(__name__)

    async def on_ready(self):
        self.log_setup()
        self.log.info("Backend running")
        self.config.role = await self.get_role()
        self.log.debug("Role set")
        for channel in self.get_all_channels():
            if channel.name == self.config.broadcast_channel:
                self.broadcast_channel = channel
                # await self.broadcast_channel.send("Bot online")

        if not self.broadcast_channel:
            self.log.error(f"Unable to set broadcast-channel: {self.config.broadcast_channel}")
            await self.close()
            exit(-1)

        self.log.debug("Broadcast-channel setup")

        self.handler_setup()

        self.log.info("Bot ready")


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
        self.log.debug(f"Raw reaction add from {reaction.id}")
        permissions = await self.get_permissions(reaction.member)
        for handler in self.reaction_handlers:
            await handler.dispatch(reaction, permissions)

    def get_member(self, id) -> discord.Member:
        member = None
        for m in self.get_all_members():
            if m.id == id:
                member = m
                break
        return member

    async def on_raw_reaction_remove(self, reaction):
        self.log.debug(f"Raw reaction remove from: {reaction.id}")
        reaction.member = self.get_member(reaction.id)
        if not reaction.member:
            return
        permissions = await self.get_permissions(reaction.member)
        for handler in self.reaction_handlers:
            await handler.dispatch(reaction, permissions)

    async def on_message(self, message):
        self.log.debug(f"Message:{message.content} from {message.author.id}")
        if message.author == self.user:
            return
        permissions = Permissions.restricted
        if isinstance(message.channel, discord.TextChannel):
            permissions = await self.get_permissions(message.author)
        elif isinstance(message.channel, discord.DMChannel):
            member = self.get_member(message.author.id)
            if member:
                permissions = await self.get_permissions(member)

        for handler in self.message_handlers:
            await handler.dispatch(message, permissions)

    async def get_permissions(self, member):
        if member.id == self.config.owner:
            return Permissions.admin
        elif self.broadcast_channel.permissions_for(member).manage_roles:
            return Permissions.member
        else:
            return Permissions.restricted


if __name__ == "__main__":
    token = ""
    token_file = "auth"
    if not os.path.isfile(token_file):
        exit("Please create a tokenfile 'auth'")
    try:
        with open(token_file) as f:
            token = f.read()
    except FileNotFoundError:
        print("Unable to read authToken")

    config = Configuration()
    client = CsBot(config)
    client.run(token)
