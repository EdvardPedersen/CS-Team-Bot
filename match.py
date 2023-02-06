import datetime
import constants
import re
import CSGO_GET_ACTIVE_DUTY
from team import roll_teams
from helper_functions import DiscordString
from mapdict import MapDict


class Match():
    def __init__(self, date, team) -> None:
        self.date = date
        self.team = team
        self.status = "active"

    def set_active(self):
        self.status = "active"

    def set_passive(self):
        self.status = "inactive"


class MatchDay():
    def __init__(self, users, num_matches=2, playday="Wednesday") -> None:
        self.players = users
        self.num_matches = num_matches
        ["ready", "open", "closed"]
        self.status = "ready"
        ["active", "inactive"]
        self.veto = "inactive"
        self.message = None
        self.banorder_message = None
        self.date = None
        self.playtime = datetime.time(hour=20, minute=00)
        self.playday = playday
        self.map_pool = CSGO_GET_ACTIVE_DUTY.get_active_duty()
        self.banned_maps = []
        self.picked_maps = []
        self.shared_banorder = []
        self.available_maps = self.map_pool.copy()
        self.weekdays = {
            'Monday': 0,
            'Tuesday': 1,
            'Wednesday': 2,
            'Thursday': 3,
            'Friday': 4,
            'Saturday': 5,
            'Sunday': 6,
        }
        self.matches = None
        self.teams = None
        self.set_playdate_next()

    def setup_teams(self):
        self.teams = roll_teams(self.players, self.num_matches)

    def setup_matches(self):
        if self.teams:
            self.matches = []
            for team in self.teams:
                self.matches.append(Match(self.date, team))

    def set_num_matches(self, num):
        self.num_matches = num

    def player_add(self, player):
        self.players[player.id] = player

    def get_status(self):
        return self.status

    def set_banorder_message(self, message):
        self.banorder_message = message

    async def refetch_message(self):
        self.message = await self.message.channel.fetch_message(self.message.id)

    async def registration_end(self, player_pool):
        reply = ""
        if self.status == "open":
            for reaction in self.message.reactions:
                u = [u async for u in reaction.users()]
                for users in u:
                    self.player_add(player_pool[users.id])
            if not self.teams:
                self.teams = roll_teams(self.players, self.num_matches)
                self.matches = [Match(self.date, team) for team in self.teams]
            self.status = "closed"
            await self.message.unpin()
            reply = "Registration closed"
        else:
            reply = "No registration active"

        return reply

    def registration_start(self, arguments, teammember_role):
        arguments = re.match("^![a-zA-Z]*\s(\d{1,2})$", arguments)
        if arguments:
            num_matches = int(arguments.group(1))
            if num_matches < 1:
                num_matches = 2
        else:
            num_matches = 2

        match self.status:
            case "open":
                raise AttributeError("open")
            case "closed":
                raise AttributeError("closed")
            case "ready":
                self.set_playdate_next()
                self.set_num_matches(num_matches)
                self.status = "open"
                return f"<@&{teammember_role.id}>\nReact to this post to sign up for the [{self.num_matches}] matches on: {self.date} **{str(self.playtime)[0:5]}**"
            case _:
                raise NameError

    async def registration_cancel(self):
        reply = ""
        if self.status == "open":
            self.reset_state()
            await self.message.unpin()
            await self.message.delete()
            self.message = None
            reply = "Cancelled registration"
        else:
            reply = "No registration active"

        return reply

    def reset_state(self):
        self.veto = "inactive"
        self.players = {}
        self.teams = None
        self.banned_maps = []
        self.picked_maps = []
        self.available_maps = self.map_pool.copy()
        self.status = "ready"

    async def delete(self):
        if self.status == "closed":
            self.reset_state()
            if self.banorder_message:
                await self.banorder_message.delete()
                self.banorder_message = None

    def next_match(self):
        reply = ""
        if self.status == "active":
            reply = f"Next match: {self.date}\nPlaying: {[player.name for player in self.players.values()]}"
        else:
            reply = "No matches found"

        return reply

    def set_playdate_next(self):
        days_in_week = len(self.weekdays.keys())
        today = datetime.date.today()
        days_to = self.weekdays[self.playday] - datetime.date.weekday(today)
        if days_to < 0:  # we are past playday this week
            days_to += days_in_week
        self.date = today + datetime.timedelta(days_to)

    def get_teamlist(self) -> str:
        teams = DiscordString("")
        for i, team in self.teams.items():
            teams += team.get_info()
        teams = teams.to_code_block("arm")
        return teams

    def banorder_formatted_message(self, format_type):
        banorders = self.banorder()
        shared = banorders['shared_banorder'].to_code_block(format_type)
        banned = banorders['banned_maps'].to_code_inline()
        message = f"**Shared banorder:**\n{shared}\nBanned maps: {banned}\n"
        return message

    def get_next_ban(self):
        for map in self.shared_banorder:
            if map in self.available_maps:
                return map

    def get_next_pick(self):
        maps = reversed(self.shared_banorder)
        for map in maps:
            if map in self.available_maps:
                return map

    async def pick(self, map):
        if self.banorder_message:
            self.available_maps.remove(map)
            self.picked_maps.append(map)
            await self.banorder_message.edit(content=self.banorder())
        else:
            print(f"Picking:{map}")

    async def unpick(self, map):
        if self.banorder_message:
            self.picked_maps.remove(map)
            self.available_maps.append(map)
            await self.banorder_message.edit(content=self.banorder())
        else:
            print(f"Unpicking:{map}")

    async def ban(self, map):
        if self.banorder_message:
            self.available_maps.remove(map)
            self.banned_maps.append(map)
            await self.banorder_message.edit(content=self.banorder())
        else:
            # TODO: log
            print(f"Banned:{map}")

    async def unban(self, map):
        if self.banorder_message:
            self.banned_maps.remove(map)
            self.available_maps.append(map)
            await self.banorder_message.edit(content=self.banorder())
        else:
            print(f"Unbanned: {map}")

    def team_to_map_fit(self):
        scores = {}
        for map in self.picked_maps:
            scores[map] = {}
            for id, team in self.teams.items():
                scores[map][id] = 0
                for player in team.players:
                    scores[map][id] += player.maps[map]
                try:
                    scores[map][id] /= len(team.players)
                except ZeroDivisionError:
                    pass
        for map in self.available_maps:
            scores[map] = {}
            for id, team in self.teams.items():
                scores[map][id] = 0
                for player in team.players:
                    scores[map][id] += player.maps[map]
                try:
                    scores[map][id] /= len(team.players)
                except ZeroDivisionError:
                    pass
        pprint = ""
        for map, teams in scores.items():
            pprint += f"{map}: "
            for team, score in teams.items():
                pprint += f"Team{team}[{score}] "
            pprint += "\n"
        return pprint

    def _get_banorder_info(self):
        '''
        Returns  dictionary with formatting:
        'private_banorders': dict{teamID<int> : Banorder<DiscordString>),..}  empty or more messages with teamID and their private banorder
        'shared_banorder': <DiscordString> empty or one message with shared  banorder for  all teams in  current  veto 
        'banned_maps': <DiscordString> empty or one  message with currently banned maps  in this veto
        'picked_maps': <DiscordString> empty or one  message with currently picked   in this veto
        'team_fit':  <DiscordString> empty or one message with team score for each map picked in veto
        '''
        messages = {
            'private_banorders': {},
            'shared_banorder': "",
            'banned_maps': "",
            'picket_maps': ""
        }
        for team_num, team in self.teams.items():
            messages['private_banorders'][team_num] = DiscordString(
                f"Team {team_num}: {[player.name for player in team.players]}\nbanorder -> {team.get_banorder()}")
        self.shared_banorder = self.get_shared_banorder()
        messages['shared_banorder'] = DiscordString(f"{self.shared_banorder}")
        messages['banned_maps'] = DiscordString(
            f"{[map for map in self.banned_maps]}")
        messages['picked_maps'] = DiscordString(
            f"{[map for map in self.picked_maps]}")
        messages['team_fit'] = DiscordString(f"{self.team_to_map_fit()}")
        return messages

    def banorder(self):
        reply = ""
        match self.status:
            case "open":
                raise AttributeError("open")
            case "closed":
                if not self.teams:
                    raise AttributeError("teams not rolled")
                banorder_info = self._get_banorder_info()
                reply += f"Shared banorder: {banorder_info['shared_banorder'].to_code_block('ml')}"
                reply += DiscordString(
                    f"Banned maps -> {banorder_info['banned_maps'].to_code_inline()}\n")
                reply += DiscordString(
                    f"Picked maps -> {banorder_info['picked_maps'].to_code_inline()}\n")
                reply += DiscordString(
                    f"{banorder_info['team_fit'].to_code_inline()}")
            case "ready":
                raise AttributeError("ready")
            case _:
                raise NameError()
        return reply

    def shared_weighted_preference(self, private_preferences):
        shared_preference = MapDict()
        for map in self.available_maps:
            shared_preference[map] = 0
            for preference in private_preferences.values():
                shared_preference[map] += preference[map]

        return shared_preference

    def teams_private_banorder_copy(self):
        preferences = MapDict()
        for teamID, team in self.teams.items():
            prefs = team.map_preference.copy()
            preferences[teamID] = prefs

        return preferences

    def get_shared_banorder(self):
        private_banorders = self.teams_private_banorder_copy()
        for banorder in private_banorders.values():
            banorder.remove_banned_maps(self.banned_maps)
            banorder.remove_picked_maps(self.picked_maps)
            banorder.amplify_most_wanted()

        shared_banorder = self.shared_weighted_preference(
            private_banorders).to_list_sorted()

        return shared_banorder

    async def pin(self):
        await self.message.pin()

    async def unpin(self):
        await self.message.unpin()

    async def reply(self, message):
        await self.message.reply(message)
