import math
import statistics
import constants
import random
from player import  Player
from mapdict import MapDict

class Team():
    def __init__(self,id,players, all_players) -> None:
        self.id = id
        self.overallcompatability = math.inf
        self.rankcompatability = 0
        self.mapcompatability = 0
        self.players = players
        self.map_preference = MapDict()
        self.set_map_preference()
        self.calculate_rank_score(all_players)
        self.calculate_map_score()
        self.calculate_overall_compatability()

    def get_info(self) -> str:
        igls = [player.name for player in self.players if player.igl]
        members = [player.name for player in self.players if not player.igl]
        return f"Team{self.id}: IGLs: {igls} Players: {members} [{self.rankcompatability}][{self.mapcompatability}][{self.overallcompatability}]\n"

    def set_map_preference(self):
        for map in constants.maps:
            self.map_preference[map] = 0
            for player in self.players:
                self.map_preference[map] += player.maps[map]
    
    def get_map_preference(self) -> MapDict:
        return self.map_preference

    def get_banorder(self) -> list:
        return sorted(self.map_preference,key=self.map_preference.get)

    def get_players(self)->list:
        return [player for player in self.players]

    def generate_random():
        players = []
        for _ in range(constants.team_size):
            players.append(Player.generate_random())
        team = Team(players)
        team.set_map_preference()
    
    def calculate_rank_score(self, all_players):
        try:
            avg_rank = statistics.mean([player.rank for player in all_players])
            avg_team = statistics.mean([player.rank for player in self.players])
        except statistics.StatisticsError:
            avg_rank = 0
            avg_team = 0
        self.rankcompatability = round(abs(avg_team - avg_rank),3)

    def calculate_map_score(self) -> float:
        total_distance = 0
        for player in self.players:
            for other_player in self.players:
                if other_player == player:
                    continue
                total_distance += player.map_compatability(other_player)
        try:
            self.mapcompatability = round((total_distance/(len(constants.maps)*len(self.players))),3)
        except ZeroDivisionError:
            self.mapcompatability = total_distance

    def calculate_overall_compatability(self):
        self.overallcompatability = self.rankcompatability + self.mapcompatability


def _choose_players(players, team_size) -> list:
    chosen = []
    
    for _ in range(team_size):
        if len(chosen) == 0:
            igls = [player for player in players if player.igl]
            applicableIgls = [igl for igl in igls if igl.matches <= min(igl.matches for igl in igls) and igl not in chosen]
            if applicableIgls:
                igl = random.choice(applicableIgls)
                chosen.append(igl)
                continue
        applicable = [player for player in players if player.matches <= min(player.matches for player in players) and player not in chosen]
        if not applicable:
            applicable = [player for player in players if player not in chosen]
        player = random.choice(applicable)
        chosen.append(player)
    return chosen

def roll_teams(players, num_matches):
    player_pool = [player for player in players.values()]
    for player in player_pool:
        player.chosen = 0
        player.matches = 0

    best_teams = {}
    team_size = constants.team_size if len(players) >= constants.team_size else len(players)
    for i in range(num_matches):
        best_score = math.inf
        best_team = None
        for _ in range(100):
            team = Team(i,_choose_players(player_pool.copy(),team_size),player_pool)
            if team.overallcompatability < best_score:
                best_score = team.overallcompatability
                best_team = team
        
        for player in best_team.players:
            player.matches += 1
        best_teams[i] = best_team
    return best_teams
