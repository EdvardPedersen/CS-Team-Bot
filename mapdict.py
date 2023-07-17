import CSGO_GET_ACTIVE_DUTY
import logging
import traceback


class MapDict(dict):

    def amplify_most_wanted(self):
        factor = len(self.keys())
        weights = [16 * factor, 8 * factor, 4 * factor]
        nmaps = 3
        top_n = self.top_n_maps(nmaps)
        for i, map in enumerate(top_n):
            self[map] *= weights[i]

    def remove_banned_maps(self, banned_maps):
        logger = logging.getLogger(f"{self.__class__.__name__}")
        for banned_map in banned_maps:
            try:
                del self[banned_map]
            except NameError as e:
                logger.debug(
                    traceback.TracebackException.from_exception(e).format())
                logger.exception(
                    f"Tried banning {banned_map} not found in available maps.")

    def remove_picked_maps(self, picked_maps):
        logger = logging.getLogger(f"{self.__class__.__name__}")
        for picked_map in picked_maps:
            try:
                del self[picked_map]
            except NameError as e:
                logger.debug(
                    traceback.TracebackException.from_exception(e).format())
                logger.exception(
                    f"Tried picking {picked_map} not found in available maps.")

    def to_list(self):
        return list(self)

    def to_list_sorted(self, reversed=False):
        return sorted(self, key=self.get, reverse=reversed)

    def top_n_maps(self, n=len(CSGO_GET_ACTIVE_DUTY.get_active_duty())):
        return sorted(self, key=self.get, reverse=True)[:n]

    def copy(self):
        _dict = MapDict()
        for key, val in self.items():
            _dict[key] = val
        return _dict
