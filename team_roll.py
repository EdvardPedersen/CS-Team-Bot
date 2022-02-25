import math
import constants
import random
from player import  Player

class Team():
    def __init__(self,players) -> None:
        self.overallcompatability = math.inf
        self.rankcompatability = 0
        self.mapcompatability = 0
        self.players = players
        self.map_preference = {}

    def set_map_preference(self):
        for map in constants.maps:
            self.map_preference[map] = 0
            for player in self.players:
                self.map_preference[map] += player.maps[map]
    
    def get_map_preference(self) -> dict:
        return self.map_preference

    def get_banorder(self) -> list:
        return sorted(self.map_preference,key=self.map_preference.get)

    def generate_random():
        players = []
        for _ in range(constants.team_size):
            players.append(Player.generate_random())
        team = Team(players)
        team.set_map_preference()

    @staticmethod
    def euclidean_distance(val1, val2):
        return math.sqrt((val1-val2)**2)

    def calculate_rank_score(self):
        total_distance = 0
        for player in self.players:
            for other_player in self.players:
                if other_player == player:
                    continue
                total_distance += self.euclidean_distance(player.rank,other_player.rank)
        self.rankcompatability = total_distance
        return total_distance

    def _calculate_map_compatability(self,p1, p2) -> float:
        diff = 0
        for map in constants.maps:
            diff += self.euclidean_distance(p1.maps[map],p2.maps[map])
        return diff

    def calculate_map_score(self) -> float:
        total_distance = 0
        for player in self.players:
            for other_player in self.players:
                if other_player == player:
                    continue
                total_distance += self._calculate_map_compatability(player, other_player)
        self.mapcompatability = total_distance
        return total_distance

    def calculate_overall_compatability(self):
        self.overallcompatability = self.rankcompatability + self.mapcompatability



def _choose_players(players, team_size) -> Team:
    chosen = []
    for _ in range(team_size):
        applicable = [player for player in players if player.matches <= min(player.matches for player in players) and player not in chosen]
        if not applicable:
            applicable = [player for player in players if player not in chosen]
        player = random.choice(applicable)
        chosen.append(player)
    return chosen

def roll_teams(players, num_matches):
    for player in players.values():
        player.chosen = 0

    player_pool = [player for player in players.values()]
    best_teams = {}
    team_size = constants.team_size if len(players) >= constants.team_size else len(players)
    for i in range(num_matches):
        best_score = math.inf
        best_team = None
        for _ in range(100):
            team = Team(_choose_players(player_pool.copy(), team_size))
            team.calculate_map_score()
            team.calculate_rank_score()
            team.calculate_overall_compatability()
            if team.overallcompatability < best_score:
                best_score = team.overallcompatability
                best_team = team
        
        best_team.set_map_preference()
        for player in best_team.players:
            player.matches += 1
        best_teams[i] = best_team
    return best_teams
