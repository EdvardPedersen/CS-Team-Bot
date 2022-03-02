import constants

class Player:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.rank = 1
        self.chosen = 0
        self.maps = {}
        for map in constants.maps:
            self.maps[map] = 0

    def set_rank(self, new_rank):
        self.rank = new_rank

    def rank_map(self, map, rank):
        self.maps[map] = rank

    def map_ranking(self):
        ranking = ""
        for map,value in self.maps.items():
            ranking += f"{map}: {value}\n"
        return ranking

    def get_info(self):
        s = f"{self.name} is rank {constants.rank[self.rank]} and has map order: |"
        for map in sorted(self.maps, key = lambda x: self.maps[x]):
            s += map + " | "
        return s
