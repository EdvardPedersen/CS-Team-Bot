
import pickle
from random import randint

import discord
import datetime
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
        self.owner = int(input("Insert your discordID\n"))
        self.super_users_id = admin
        self.super_users_id.append(self.owner)
        self.server = server
        self.team_role = role
        self.guild = ""
        self.role = ""


class Registration():
    def __init__(self,users,date=None) -> None:
        self.date = None
        self.playdate_next(date)
        self.users = users
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
            days_in_week = 7
            today = datetime.date.today()
            # weekday 2 = wednesday, please change this magic number
            days_to = weekdays[playday] - datetime.date.weekday(today)
            if days_to <= 0: # we are past playday this week
                days_to += days_in_week
            self.date =  today + datetime.timedelta(days_to)

    def set_active(self):
        self.status = True

    def set_passive(self):
        self.status = False

class CsBot(discord.Client):
    def __init__(self, config):
        intents = discord.Intents.default()
        intents.members = True
        intents.reactions = True
        super().__init__(intents=intents)
        self.config = config
        self.registration_active = False
        self.registration_previous = None # this should probably load some DB/Disk previous registration
        self.registration_next = None
        self.registration_post = None
        self.broadcast_channel = None
        self.record = None

    async def set_registration_previous(self):
        if self.record:
            least = list(self.record.keys())[0]
            for record in self.record.keys():
                if record >= datetime.date.today() and record < least:
                    print(record)
                    least = record
            self.registration_previous = self.record[least]


    async def on_ready(self):
        self.config.role = await self.get_role()
        for channel in self.get_all_channels():
            if channel.name == "general":
                self.broadcast_channel = channel
        
        if not self.broadcast_channel:
            print("Could not set broadcast_channel")

        await self.read_prev_state()
        await self.set_registration_previous()
        
        # await self.broadcast_channel.send("Hello, I'm CS-Bot")

    async def get_role(self):
        for g in self.guilds:
            for r in g.roles:
                if r.id == self.config.team_role:
                    self.config.guild = g
                    print(r.members)
                    return r

    async def on_raw_reaction_add(self, reaction):
        '''
        Everyone can react to a message, but only registrated team members
        will be added to the lineup
        '''
        if self.registration_active:
            if await self.get_permissions(reaction.member) > 1:
                if reaction.message_id == self.registration_post.id:
                    self.registration_next.users[reaction.user_id] = reaction.member.name
            else:
                await reaction.member.send("You have not signed up for the coming season: <Follow this guideline>")

    async def on_raw_reaction_remove(self, reaction):
        '''
        This reaction removal does not require permission check as we only care for
        the registration message and that the reacting people have a given role

        BUT reactions can be added by anyone... so we need it?
        '''
        if self.registration_active:
            if await self.get_permissions(reaction.member) > 1:
                if reaction.message_id == self.registration_post.id:
                    self.registration_next.users.pop(reaction.user_id)

    async def on_message(self, message):
        if message.author == self.user:
            return
        permissions = await self.get_permissions(message.author)
        if message.content == "!register":
            if permissions == 3:
                if self.registration_active:
                    await message.author.send("Registration already active, please cancel previous registration to start a new.")
                else:
                    await self.registration_start()

        elif message.content.startswith("!register "):
            if permissions == 3:
                if self.registration_active:
                    await message.author.send("Registration already active, please cancel previous registration to start a new.")
                else:
                    await self.registration_start(message.content.removeprefix("!register "))

        if message.content == "!signup":
            await message.author.add_roles(await self.get_role())

        if message.content == "!optout":
            await message.author.remove_roles(await self.get_role())
        if message.content.startswith("!cancel"):
            if permissions == 3:
                if self.registration_active:
                    await self.registration_cancel()
                else:
                    await message.author.send("No active registration.")

        if message.content == "!end":
            if permissions == 3:
                if not self.registration_active:
                    await message.author.send("No registration active.")
                else:
                    await self.registration_end()

        if message.content == "!next":
            if not self.registration_previous:
                await self.broadcast_channel.send("No registration for next match")
            else:
                await self.match_print_next()

        if message.content == "!upcoming":
            upcoming = ["**"+ upcoming.date.strftime("%Y-%m-%d")+"**" for upcoming in self.record.values() if upcoming.date > datetime.date.today()]
            upcoming = sorted(upcoming)
            await self.broadcast_channel.send(f"Registrated upcoming matches: {upcoming}")

        if message.content == "!maps":
            if permissions > 1:
                await message.author.send("You can register preferences here")
            else:
                await message.author.send("You do not have permission to register map preferences")

        if message.content.startswith("!purge"):
            if permissions == 3:
                await self.registration_purge(message.content)

        if message.content == "!easterEgg":
            if permissions == 3:
                await self.broadcast_channel.purge()

        if message.content == "!dank":
            if permissions > 1:
                await self.broadcast_channel.send(f"Brought to you by HenkeBazZ\nhttps://www.youtube.com/watch?v=q6EoRBvdVPQ&list=PLFsQleAWXsj_4yDeebiIADdH5FMayBiJo&index=1")
    
        if message.content.startswith("!setAdmin"):
            if permissions == 3:
                IDs = message.content.removeprefix("!setAdmin ")
                IDs = IDs.split()
                for user in IDs:
                    self.config.super_users_id.append(int(user))

        if message.content.startswith("!removeAdmin"):
            if permissions == 3:
                IDs = message.content.removeprefix("!removeAdmin")
                IDs = IDs.split()
                for id in IDs:
                    if int(id) != self.config.owner:
                        self.config.super_users_id.remove(int(id))

        if message.content == "!admins":
            admins = [admin.name for admin in self.get_all_members() if admin.id in self.config.super_users_id]
            await self.broadcast_channel.send(f"Adminlist: {admins}")


    async def registration_start(self,date=None):
        '''
        Start a registration for next playdate
        If date for next playdate matches the previous one, the previous registration 
        have to be manually deleted before trying again
        '''
        if date:
            year,month,day = date.split('-')
            date = datetime.date(int(year),int(month),int(day))
        self.registration_next = Registration({},date)
        self.registration_active = True
        self.registration_post = await self.broadcast_channel.send(f"```cpp\n# please react to this post to sign up for the match on:\n{self.registration_next.date}```")


    async def registration_purge(self, message):
        message = message.removeprefix("!purge ")
        year,month,day = message.split('-')
        date = datetime.date(int(year),int(month),int(day))
        try:
            self.record.pop(date)
            if self.registration_previous.date == date:
                self.registration_previous = None
                await self.set_registration_previous()
        except KeyError:
            print("Invalid purge date")
        await self.write_prev_state()

    async def registration_cancel(self):
        '''
        Cancel the ongoing registration
        '''
        self.registration_next = None
        await self.registration_post.delete()
        self.registration_post = None
        self.registration_active = False

    async def match_print_next(self):
        playing = list(self.registration_previous.users.values())
        if self.registration_previous.date < datetime.date.today():
            await self.broadcast_channel.send("No planned match")
        else:
            await self.broadcast_channel.send(f"Date: **[{self.registration_previous.date}]**\nPlaying: {playing}")

    async def read_prev_state(self):
        try:
            with open("previous","rb") as f:
                r = f.read()
                self.record = pickle.loads(r)
        except IOError as ioerr:
            with open("previous","wb") as f:
                pass
            self.record = {}

    async def write_prev_state(self):
        try:
            with open("previous","wb") as f:
                r = pickle.dumps(self.record)
                f.write(r)
        except IOError as ioerr:
            print(ioerr)

    async def registration_end(self):
        '''
        This should probably store some state on disk, update last registration and 
        enable starting of a new registration
        '''
        if self.registration_next: # if new registration
            self.registration_previous = self.registration_next
            self.record[self.registration_previous.date] = self.registration_previous    
        else:
            self.record[self.registration_previous.date] = self.registration_previous
        await self.write_prev_state()
        await self.registration_post.delete()
        self.registration_post = None
        self.registration_next = None
        self.registration_active = False


    async def get_permissions(self, user):
        if user.id in self.config.super_users_id:
            return 3
        if user in self.config.role.members:
            return 2
        return 1
        


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
    print("No admins added, only owner has access to core features")


config = Configuration(admins, 875845075068944424, 941396110252060702)
client = CsBot(config)
client.run(token)
