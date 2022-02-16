import math
import constants
import random


def choose_team(players):
    chosen = []
    k = 5 if len(players)>5 else len(players)
    for i in range(k):
        applicable = [player for player in players.values() if player.chosen <= min([player.chosen for player in players.values()]) and player not in chosen]
        player = random.choice(applicable)
        chosen.append(player)
        player.chosen += 1

    for player in players.values():
        player.chosen = 0
    return chosen


def roll_teams(players, num_matches):
    best_teams = []
    for i in range(num_matches):
        best_teams.append(choose_team(players))

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
