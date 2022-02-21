import math
import constants
import random

def _choose_players(players, team_size) -> list:
    chosen = []
    for _ in range(team_size):
        applicable = [player for player in players if player.chosen <= min([player.chosen for player in players])]
        player = random.choice(applicable)
        player.chosen += 1
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
        for _ in range(100):
            team = _choose_players(player_pool.copy(), team_size)
            score = _calculate_average_distance(team)
            if score < best_score:
                best_score = score
                best_teams[i] = team

        for player in player_pool:
            for chosen_player in best_teams[i]:
                if player.id == chosen_player.id:
                    player.chosen += 1

    print(type(best_teams))
    return best_teams

def _calculate_map_compatability(p1, p2) -> float:
    diff = 0
    for map in constants.maps:
        diff += (p1.maps[map] - p2.maps[map]) ** 2
    return math.sqrt(diff)

def _calculate_average_distance(players) -> float:
    total_distance = 0
    for player in players:
        for other_player in players:
            if other_player == player:
                continue
            total_distance += _calculate_map_compatability(player, other_player)
    return total_distance

def get_ban_order(teams) -> str:
    #idea : weight the 3 most wanted maps for each team with decreasing
    #weights,ie:(10,5,2) to pull out wanted maps from the dataset
    #sum the two distributions together and select the lowest ranked
    banorder = "**Banorder:**\n"
    for i,team in teams.items():
        i += 1
        banorder += f"Team {i}: "
        b = {}
        for map in constants.maps:
            b[map] = 0
            for player in team:
                b[map] += player.maps[map]
        s = [map for map in sorted(b,key=lambda k:b[k])]
        banorder += f"{s}\n"
    
    return banorder
