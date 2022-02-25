import constants
import random

class Player:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.rank = 1
        self.matches = 0
        self.maps = {}
        for map in constants.maps:
            self.maps[map] = 0

    def set_rank(self, new_rank):
        self.rank = new_rank

    def rank_map(self, map, rank):
        self.maps[map] = rank

    def map_ranking(self) -> str:
        ranking = ""
        for map,value in self.maps.items():
            ranking += f"{map}: {value}\n"
        return ranking

    def get_info(self):
        s = f"{self.name} is rank {constants.rank[self.rank]} and has map order: |"
        for map in sorted(self.maps, key = lambda x: self.maps[x]):
            s += map + " | "
        return s

    def generate_random():
        id = random.randint(0,0xFFFFFFFF)
        player = Player(id,str(id))
        player.rank = random.randint(1,18)
        player.maps = {}
        map_pool = random.sample(constants.maps,k=len(constants.maps))
        for i,map in enumerate(map_pool):
            player.maps[map] = i

        return player