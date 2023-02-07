import constants
import random

from CSGO_GET_ACTIVE_DUTY import get_active_duty
from helper_functions import euclidean_distance, DiscordString
from mapdict import MapDict


class Player:
    def __init__(self, id, name, sname):
        self.id = id
        self.screen_name = sname
        self.name = name
        self.rank = 1
        self.title = constants.ranks[self.rank]
        self.matches = 0
        self.maps = MapDict()
        self.igl = False
        for map in get_active_duty():
            self.maps[map] = 0

    def set_igl(self, val: bool):
        self.igl = val

    def set_rank(self, new_rank):
        self.rank = new_rank
        self.title = constants.ranks[self.rank]

    def rank_map(self, map, rank):
        self.maps[map] = rank

    def get_map_ranking(self) -> str:
        ranking = ""
        for map, value in self.maps.items():
            ranking += f"{map}: {value}\n"
        return ranking

    def map_order(self):
        order = DiscordString("| ")
        for map in self.maps.to_list_sorted():
            order += f"{map} | "
        return order.to_code_inline()

    def get_info(self):
        s = f"{self.name} is rank {self.title} and has map order: "
        s += self.map_order()
        return s

    def rank_compatability(self, player) -> float:
        return euclidean_distance(self.rank, player.rank)

    def map_compatability(self, player) -> float:
        diff = 0
        for map in get_active_duty():
            diff += euclidean_distance(self.maps[map], player.maps[map])
        return diff

    def generate_random(id=random.randint(0, 0xFFFFFFFF)):
        player = Player(id, str(id))
        player.rank = random.randint(1, 18)
        player.maps = {}
        map_pool = random.sample(get_active_duty(), k=len(get_active_duty()))
        for i, map in enumerate(map_pool):
            player.maps[map] = i

        return player
