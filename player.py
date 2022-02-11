import constants

class Player:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.rank = 0
        self.maps = {}
        for map in constants.maps:
            self.maps[map] = 0

    def set_rank(self, new_rank):
        self.rank = new_rank

    def rank_map(self, map, rank):
        self.maps[map] = rank

    def get_info(self):
        s = f"{self.name} is rank {constants.rank[self.rank]} and has map order: |"
        for map in sorted(self.maps, key = lambda x: self.maps[x]):
            s += map + " | "
        return s
