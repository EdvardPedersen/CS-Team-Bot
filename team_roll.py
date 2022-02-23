import math
import constants
import random
from player import  Player

class Team():
    def __init__(self,players) -> None:
        self.overallcompatability = 0
        self.rankcompatability = 0
        self.mapcompatability = 0
        self.players = players
        self.map_preference = {}

    def set_map_preference(self):
        for map in constants.maps:
            self.map_preference[map] = 0
            for player in self.players:
                self.map_preference[map] += player.maps[map]
    
    def get_map_preference(self):
        return self.map_preference


def _choose_players(players, team_size, playing) -> list:
    chosen = []
    not_matched = [player for player in players if player not in playing]
    for _ in range(team_size):
        applicable = [player for player in not_matched if player.chosen <= min(player.chosen for player in not_matched) and player not in chosen]
        if not applicable:
            applicable = [player for player in players if player.chosen <= min(player.chosen for player in players) and player not in chosen]
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
    playing = []
    for i in range(num_matches):
        best_score = math.inf
        best_team = Team(None)
        for _ in range(100):
            team = _choose_players(player_pool.copy(), team_size,playing)
            mapscore = _calculate_map_distance(team)
            rankscore = _calculate_rank_distance(team)
            score = rankscore + mapscore
            if score < best_score:
                best_score = score
                best_team.players = team
                best_team.mapcompatability = mapscore
                best_team.rankcompatability = rankscore
                best_team.overallcompatability = score
        
        best_team.set_map_preference()
        best_teams[i] = best_team
        for player in best_team.players:
            playing.append(player)
    return best_teams


def _euclidean_distance(val1, val2):
    return math.sqrt((val1-val2)**2)


def _calculate_rank_distance(players):
    total_distance = 0
    for player in players:
        for other_player in players:
            if other_player == player:
                continue
            total_distance += _euclidean_distance(player.rank,other_player.rank)
        
    return total_distance
def _calculate_map_compatability(p1, p2) -> float:
    diff = 0
    for map in constants.maps:
        diff += (p1.maps[map] - p2.maps[map]) ** 2
    return math.sqrt(diff)

def _calculate_map_distance(players) -> float:
    total_distance = 0
    for player in players:
        for other_player in players:
            if other_player == player:
                continue
            total_distance += _calculate_map_compatability(player, other_player)
    return total_distance


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

def remove_banned_maps(map_preferences, banned_maps):
    for banned_map in banned_maps:
        for maps in map_preferences.values():
            del maps[banned_map]

def sum_weighted_preferences(preferences):
    sum = {}
    for maps in preferences.values():
        for map,score in maps.items():
            try:
                sum[map] += score
            except KeyError:
                sum[map] = score

    return sum
def get_ban_order(teams,banned_maps):
    map_preferences = {}
    for i, team in teams.items():
        map_preferences[i] = team.map_preference.copy()

    remove_banned_maps(map_preferences,banned_maps)

    amplify_most_wanted(map_preferences)

    banorder = sum_weighted_preferences(map_preferences)
    
    return sorted(banorder,key=banorder.get)

def test_banorder():
    log = "**Test Banorder Log**\n"
    players = {}
    for i in range(5):
        player = Player(i,f"{i}")
        player.rank = random.randint(1,18)
        for j,map in enumerate(constants.maps):
            player.maps[map] = j
        players[i] = player
    for i in range(5,14,1):
        player = Player(i,f"{i}")
        player.rank = random.randint(1,18)
        maps = random.sample(constants.maps,len(constants.maps))
        for j,map in enumerate(maps):
            player.maps[map] = len(constants.maps) - j
        players[i] = player

    teams = roll_teams(players,3)

    for number,team in teams.items():
        print(f"team{number}:{[player.id for player in team.players]}")

    for i, team in teams.items():
        log += f"**Team{i}**: {team.map_preference}\nTop 3 maps:{sorted(team.map_preference,key=team.map_preference.get,reverse=True)[:3]}\n->Private banorder: {sorted(team.map_preference,key=team.map_preference.get)}\n\n"
    
    available_maps = constants.maps.copy()
    banned_maps = []
    log += "\nStart Veto(HomeTeam ban first):\n"
    for i in range(5):
        log += f"Round {i}\n"
        banorder = get_ban_order(teams,banned_maps)
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
    return log