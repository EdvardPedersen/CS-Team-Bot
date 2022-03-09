import constants

class MapDict(dict):


    def amplify_most_wanted(self):
        factor = len(self.keys())
        weights = [16*factor,8*factor,4*factor]
        nmaps = 3
        top_n = self.top_n_maps(nmaps)
        for i,map in enumerate(top_n):
            self[map] *=  weights[i]

    def remove_banned_maps(self, banned_maps):
        for banned_map in banned_maps:
            try:
                del self[banned_map]
            except NameError:
                # TODO log it
                pass

    def remove_picked_maps(self, picked_maps):
        for picked_map in picked_maps:
            try:
                del self[picked_map]
            except NameError:
                #TODO log it
                pass

    def to_list(self):
        return list(self)

    def to_list_sorted(self, reversed=False):
        return sorted(self, key=self.get, reverse=reversed)

    def top_n_maps(self, n=len(constants.maps)):
        return sorted(self, key=self.get, reverse=True)[:n]

    def copy(self):
        _dict = MapDict()
        for key,val in  self.items():
            _dict[key] = val
        return _dict