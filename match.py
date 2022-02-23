import datetime
import constants
from team_roll import roll_teams, get_ban_order, test_banorder


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
            i += 1
            teams += f"Team {i}:{[player.name for player in team.players]}\n"
        return teams

    def ban(self, map):
        self.banned_maps.append(map)

    def unban(self, map):
        self.banned_maps.remove(map)

    def banorder(self):
        message = "**Banorder**\n"
        banorder = get_ban_order(self.teams, self.banned_maps)
        message += f"{banorder}\n"
        return message

    def test_banorder(self):
        return test_banorder()
