import discord
'''
Interface:

!register - start registration for this weeks' match
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
    def __init__(self, admin, server, role):
        self.super_user = admin
        self.server = server
        self.team_role = role
        self.guild = ""
        self.role = ""

class CsBot(discord.Client):
    def __init__(self, config):
        intents = discord.Intents.default()
        intents.members = True
        intents.reactions = True
        super().__init__(intents=intents)
        self.config = config
        self.registration_active = False
        self.registered_users = {}
        self.registration_post = ""

    async def on_ready(self):
        self.config.role = await self.get_role()
        pass

    async def get_role(self):
        for g in self.guilds:
            for r in g.roles:
                if r.id == self.config.team_role:
                    self.config.guild = g
                    print(r.members)
                    return r

    async def on_raw_reaction_add(self, reaction):
        pass

    async def on_message(self, message):
        if message.author == self.user:
            return
        permissions = await self.get_permissions(message.author)
        if message.content.startswith('!register'):
            if permissions == 3:
                await self.start_registration()
            else:
                await message.channel.send("You do not have permission to start match registration")
        if message.content.startswith("!maps"):
            if permissions > 1:
                await message.author.send("You can register preferences here")
            else:
                await message.author.send("You do not have permission to register map preferences")

    async def start_registration(self):
        self.registered_users = {}
        self.registration_active = True
        self.registration_post = await self.channel.send("Please react to this post to sign up for the next match.")

    async def get_permissions(self, user):
        if user.id == self.config.super_user:
            return 3
        if user in self.config.role.members:
            return 2
        return 1
        


token = ""
with open("auth") as f:
    token = f.read()



config = Configuration(188422488080777217, 875657026775158805, 878372503196676106)
client = CsBot(config)
client.run(token)
