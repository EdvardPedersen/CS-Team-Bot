import math
import constants
import random

def roll_teams(players, matches):
    players = list(players.items())
    best_teams = [[],[]]
    played = []
    k = (len(players) if len(players)<5 else 5)
    for i in range(matches):
        best_score = math.inf
        for y in range(100):
            team = random.choices(players, k=k)
            score = _calculate_average_distance(team)
            if score < best_score:
                if i == 0:
                    best_score = score
                    played = team
                    best_teams[i] = [player[1].name for player in team]
    return best_teams

def _calculate_map_compatability(p1, p2):
    diff = 0
    for map in constants.maps:
        diff += (p1.maps[map] - p2.maps[map]) ** 2
    return math.sqrt(diff)

def _calculate_average_distance(players):
    total_distance = 0
    for i, player in players:
        for other_player in players[i:]:
            total_distance += _calculate_map_compatability(player, other_player)
    return total_distance

def get_ban_order(teams):
    pass
