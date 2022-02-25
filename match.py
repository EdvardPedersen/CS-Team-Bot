import datetime
import random
import constants
from player import Player
from team_roll import roll_teams


class Match():
    def __init__(self,date,team) -> None:
        self.date = date
        self.team = team
        self.status = "active"

    def set_active(self):
        self.status = "active"

    def set_passive(self):
        self.status = "inactive"


class MatchDay():
    def __init__(self,users,num_matches=2,date=None,playday="Wednesday") -> None:
        self.players = users
        self.num_matches = num_matches
        self.message = None
        self.banorder_message = None
        self.date = None
        self.playday = playday
        self.map_pool = constants.maps
        self.banned_maps = []
        self.weekdays = {
                'Monday':0,
                'Tuesday':1,
                'Wednesday':2,
                'Thursday':3,
                'Friday':4,
                'Saturday':5,
                'Sunday':6,
            }
        self.status = "active"
        self.matches = None
        self.teams = None
        self.playdate_next(date)

    def setup_teams(self):
        if not self.teams:
            self.teams = roll_teams(self.players,self.num_matches)
            self.matches = [Match(self.date,team) for team in self.teams]

    def set_message(self,message):
        self.message = message

    def playdate_next(self,date):
        if date:
            self.date = date
        else:
            days_in_week = len(self.weekdays.keys())
            today = datetime.date.today()
            days_to = self.weekdays[self.playday] - datetime.date.weekday(today)
            if days_to < 0: # we are past playday this week
                days_to += days_in_week
            self.date =  today + datetime.timedelta(days_to)

    def get_teamlist(self) -> str:
        teams = ""
        for i,team in self.teams.items():
            teams += f"Team {i}:{[player.name for player in team.players]}\n"
        return teams

    async def ban(self, maps):
        if not self.banorder_message:
            return
        for map in maps:
            self.banned_maps.append(map)
        await self.banorder_message.edit(content=self.banorder())

    async def unban(self, maps):
        if not self.banorder_message:
            return
        for map in maps:
            self.banned_maps.remove(map) 
        await self.banorder_message.edit(content=self.banorder())

    def banorder(self):
        message = "**Private banorders:**\n"
        for team_num,team in self.teams.items():
            message += f"```ml\nTeam {team_num}: {[player.name for player in team.players]}\nbanorder -> {team.get_banorder()}```"
        message += "**Shared banorder:**\n"
        shared_banorder = self.get_shared_ban_order(self.teams, self.banned_maps)
        message += f"```{shared_banorder}```\n"
        message += f"`Banned Maps: {[map for map in self.banned_maps]}`\n"
        return message

    def test_banorder(self):
        return test_banorder()

    @staticmethod
    def get_shared_ban_order(teams,banned_maps):
        map_preferences = {}
        for i, team in teams.items():
            map_preferences[i] = team.map_preference.copy()

        MatchDay.remove_banned_maps(map_preferences,banned_maps)
        MatchDay.amplify_most_wanted(map_preferences)
        banorder = MatchDay.sum_weighted_preferences(map_preferences)
        
        return sorted(banorder,key=banorder.get)

    @staticmethod
    def amplify_most_wanted(map_preferences):
        factor = len(map_preferences.keys())
        weights = [16*factor,8*factor,4*factor]
        nmaps = 3
        teamtopmaps = {}

        for team_num,maps in map_preferences.items():
            teamtopmaps[team_num] = [map for map in sorted(maps, key=maps.get, reverse=True)][:nmaps]

        for team, maps in teamtopmaps.items():
            for i,map in enumerate(maps):
                map_preferences[team][map] *= weights[i]

    @staticmethod
    def remove_banned_maps(map_preferences, banned_maps):
        for banned_map in banned_maps:
            for maps in map_preferences.values():
                del maps[banned_map]
    
    @staticmethod
    def sum_weighted_preferences(map_preferences):
        sum = {}
        for maps in map_preferences.values():
            for map,score in maps.items():
                try:
                    sum[map] += score
                except KeyError:
                    sum[map] = score

        return sum

def test_banorder():
    '''
    Replies back to discord client is limited to 
    2000bits or roughly 3 teams
    '''
    log = "**Test Banorder Log**\n"
    players = {}
    for i in range(8):
        players[i]=Player.generate_random()

    teams = roll_teams(players,3)

    for number,team in teams.items():
        print(f"team{number}:{[player.id for player in team.players]}\n")

    for i, team in teams.items():
        log += f"**Team{i}**: {team.map_preference}\nTop 3 maps:{sorted(team.map_preference,key=team.map_preference.get,reverse=True)[:3]}\n->Private banorder: {sorted(team.map_preference,key=team.map_preference.get)}\n\n"
    
    available_maps = constants.maps.copy()
    banned_maps = []
    log += "\nStart Veto(HomeTeam ban first):\n"
    for i in range(5):
        log += f"Round {i}\n"
        banorder = MatchDay.get_shared_ban_order(teams,banned_maps)
        log += f"**Banorder:**\n{banorder}\n"
        if i%2:
            to_ban = random.sample(available_maps,k=1)[0]
            log += f"Randomly choose to ban {to_ban}\n"
        else:
            to_ban = banorder[0]
            log += f"Based on preferences, banning:{to_ban}\n"
        available_maps.remove(to_ban)
        banned_maps.append(to_ban)
        log += f"Banned maps:{banned_maps}\nAvailable maps:{available_maps}\n"
    print(len(log))
    return log
