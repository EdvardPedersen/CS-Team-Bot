import os
import re
import pickle
import traceback
import constants
from CSGO_GET_ACTIVE_DUTY import get_active_duty
from generic_message_handler import GenericMessageHandler
from helper_functions import DiscordString, member_check, log_message, list_active_duty, list_ranks
from mapdict import MapDict
from player import Player
from match import MatchDay


def persist_state(function):
    async def persist_state(self, message):
        await function(self, message)
        self.log.info("Persisting state...")
        with open(self.persist_file, "wb") as f:
            pickle.dump(self.player_pool, f)
        self.log.info("State written.")
    return persist_state


class RegistrationHandler(GenericMessageHandler):
    def __init__(self, teammember_role, persist_file, help_text, response, reply_private, log_level):
        super().__init__(help_text, response, reply_private, log_level)
        self.teammember_role = teammember_role
        self.broadcast_channel = None
        self.persist_file = persist_file
        self.teammembers = None
        self.matchday = MatchDay({})
        self.player_pool = {}
        self.read_state()

    def read_state(self):
        self.log.info("Reading player state")
        try:
            with open(self.persist_file, "rb") as f:
                self.player_pool = pickle.load(f)
        except FileNotFoundError:
            with open(self.persist_file, "wb") as f:
                self.log.info(f"Created playerdb: {self.persist_file}")
                pass
        except EOFError:
            fSize = os.stat(self.persist_file).st_size
            match fSize:
                case 0:
                    self.log.warning("EOF, empty player db")
                case _:
                    self.log.error("EOF, likely corrupt player db")
        except Exception as e:
            self.log.exception("Unexpected exception")
            self.log.debug(
                f"{traceback.TracebackException.from_exception(e).format()}")

    @member_check
    @log_message
    async def message_list_players(self, message):
        players_message = "UiT Players: \n"
        for player in self.player_pool.values():
            players_message += f"{player.get_info()}\n"
        await self.reply(message, players_message)

    @member_check
    @log_message
    async def message_banorder(self, message):
        if self.matchday.veto == "active":
            await self.matchday.banorder_message.reply(":arrow_up:")
        else:
            try:
                m = await self.reply(message, self.matchday.banorder())
                self.matchday.set_banorder_message(m)
                self.matchday.veto = "active"
            except AttributeError as err:
                await self.reply(message, f"Matchday registration status: {err}")
            except NameError:
                await self.reply(message, "Matchday  is in invalid state")

    @member_check
    @log_message
    async def message_playday(self, message):
        args = re.match("^![a-zA-Z]+$", message.content)
        if not args:
            return
        await self.reply(message, f"Playday: {self.matchday.playday}")

    @member_check
    @log_message
    async def message_playtime(self, message):
        args = re.match("^![a-zA-Z]+$", message.content)
        if not args:
            return
        await self.reply(message, f"Playtime: {str(self.matchday.playtime)[0:5]}")

    @member_check
    @log_message
    async def message_register(self, message):
        try:
            self.matchday.message = await self.reply(message, self.matchday.registration_start(message.content, self.teammember_role))
        except AttributeError as err:
            self.log.warning(f"Registration already {err}")
            await self.matchday.reply(f'Registration is already {err}\n')
        except NameError:
            self.log.critical("Registration in invalid state")
            await self.reply(message, "Registration in invalid state\n")

    @member_check
    @log_message
    async def message_cancel(self, message):
        await self.reply(message, await self.matchday.registration_cancel())

    @member_check
    @log_message
    async def message_close(self, message):
        if self.matchday.veto == "active":
            return
        else:
            await self.matchday.refetch_message()
            await self.reply(message, await self.matchday.registration_end(self.player_pool))
            await self.reply(message, self.matchday.get_teamlist())
            m = await self.reply(message, self.matchday.banorder())
            self.matchday.set_banorder_message(m)
            self.matchday.veto = "active"

    @member_check
    @log_message
    async def message_next(self, message):
        await self.reply(message, self.matchday.next_match())

    @member_check
    @log_message
    async def message_end(self, message):
        await self.matchday.delete()

    @member_check
    @log_message
    async def message_teams(self, message):
        if not self.matchday:
            await self.reply(message, "No matches found")
        else:
            await self.reply(message, self.matchday.get_teamlist())

    @member_check
    @persist_state
    @log_message
    async def reaction_add(self, reaction):
        if self.matchday.message and self.matchday.message.id == reaction.message_id:
            if reaction.user_id not in self.player_pool:
                self.player_pool[reaction.user_id] = Player(
                    reaction.user_id, reaction.member.name)
                await reaction.member.send("Please register your rank with '!rank' and map-preferences with '!maps'")

    def rank_list(self):
        r = ""
        for rank, title in constants.ranks.items():
            r += f"{rank}: {title}\n"
        return r

    @member_check
    @persist_state
    @log_message
    async def message_rank(self, message):
        res = re.match("^![a-zA-Z]+\s(\d{1,})", message.content)
        if not res:
            await message.author.send("Please set rank with '!rank ' followed by rank number")
            await message.author.send(f"Ranks:\n{self.rank_list()}")
            return

        rank = int(res.group(1))
        if not rank:
            await message.author.send("Please set rank with '!rank ' followed by a rank number")
            return
        if rank > 18 or rank < 1:
            await message.author.send("Invalid rank")
            return
        if message.author.id not in self.player_pool:
            player = Player(message.author.id, message.author.name)
            player.set_rank(rank)
            self.player_pool[player.id] = player
        else:
            player = self.player_pool[message.author.id]
            player.set_rank(rank)
        await message.author.send(f"Your registered rank: {constants.ranks[player.rank]}")

    @member_check
    @log_message
    async def message_player_info(self, message):
        IDarg = re.match("^![a-zA-Z_]*\s*([\d]+)$", message.content)
        NameArg = re.match("^![a-zA-Z_]+\s+([a-zA-Z\d]+)$", message.content)
        if IDarg:
            id = int(IDarg.group(1))
            try:
                p = self.player_pool[id]
                await self.reply(message, p.get_info())
            except KeyError:
                await self.reply(message, "Player not found")
        elif NameArg:
            name = NameArg.group(1)
            for id, player in self.player_pool.items():
                if name == player.name:
                    await self.reply(message, player.get_info())
                    break
        else:
            try:
                p = self.player_pool[message.author.id]
                await self.reply(message, p.get_info())
            except KeyError:
                await self.reply(message, "Please register")

    @member_check
    @persist_state
    @log_message
    async def message_igl_add(self, message):
        IDarg = re.match("^![a-zA-Z_]*\s*([\d]+)$", message.content)
        NameArg = re.match("^![a-zA-Z_]+\s+([a-zA-Z\d]+)$", message.content)
        if IDarg:
            id = int(IDarg.group(1))
            try:
                p = self.player_pool[id]
                p.set_igl(True)
                await self.reply(message, f"{p.name} set to IGL")
            except KeyError:
                await self.reply(message, "Player not found")
        elif NameArg:
            name = NameArg.group(1)
            for id, player in self.player_pool.items():
                if name == player.name:
                    player.set_igl(True)
                    await self.reply(message, f"{player.name} set to IGL")
                    break
        else:
            try:
                p = self.player_pool[message.author.id]
                p.set_igl(True)
                await self.reply(message, f"{p.name} set to IGL")
            except KeyError:
                await self.reply(message, "Please register")

    @member_check
    @persist_state
    @log_message
    async def message_igl_remove(self, message):
        IDarg = re.match("^![a-zA-Z_]*\s*([\d]+)$", message.content)
        NameArg = re.match("^![a-zA-Z_]+\s+([a-zA-Z\d]+)$", message.content)
        if IDarg:
            id = int(IDarg.group(1))
            try:
                p = self.player_pool[id]
                p.set_igl(False)
                await self.reply(message, f"{p.name} removed as IGL")
            except KeyError:
                await self.reply(message, "Player not found")
        elif NameArg:
            name = NameArg.group(1)
            for id, player in self.player_pool.items():
                if name == player.name:
                    player.set_igl(False)
                    await self.reply(message, f"{player.name} removed as IGL")
                    break
        else:
            try:
                p = self.player_pool[message.author.id]
                p.set_igl(False)
                await self.reply(message, f"{p.name} removed as IGL")
            except KeyError:
                await self.reply(message, "Please register")

    @member_check
    @log_message
    async def message_list_active_duty(self, message):
        await self.reply(message, list_active_duty().to_code_inline())

    @member_check
    @log_message
    async def message_list_ranks(self, message):
        await self.reply(message, list_ranks().to_code_inline())

    def _list_maps(self) -> str:
        mapslist = ""
        for map in get_active_duty():
            mapslist += f"{map} "
        return mapslist

    @member_check
    @persist_state
    @log_message
    async def message_maps(self, message):
        if message.author.id not in self.player_pool:
            player = Player(message.author.id, message.author.name)
            self.player_pool[player.id] = player
        res = message.content.split(' ')[1:]
        if len(res) != 7:
            self.log.debug(f"Invalid list of maps: {res}")
            await self.reply(message, f"Please give map preference as a space-separated list from most wanted to least wanted map like:\n {DiscordString(f'!maps {self._list_maps()}').to_code_inline()}")
            return
        player = self.player_pool[message.author.id]
        try:
            tmpmap = MapDict()
            for i in range(len(get_active_duty())):
                if not res[i] in get_active_duty():
                    raise KeyError(f"{res[i]}")
                tmpmap[res[i]] = len(get_active_duty()) - i
            for map in get_active_duty():
                if map not in tmpmap.keys():
                    tmpmap[map] = 0
            player.maps = tmpmap
            await self.reply(message, DiscordString(f"{player.maps}").to_code_block("ml"))
        except Exception as e:
            self.log.exception(f"Invalid map name: {e}")
            await message.author.send(f"Invalid map name {e}")

    @member_check
    @log_message
    async def message_ban(self, message):
        maps = message.content.split(' ')[1:]
        for map in maps:
            await self.matchday.ban(map)

    @member_check
    @log_message
    async def message_unban(self, message):
        maps = message.content.split(' ')[1:]
        for map in maps:
            await self.matchday.unban(map)

    @member_check
    @log_message
    async def message_pick(self, message):
        maps = message.content.split(' ')[1:]
        for map in maps:
            await self.matchday.pick(map)

    @member_check
    @log_message
    async def message_unpick(self, message):
        maps = message.content.split(' ')[1:]
        for map in maps:
            await self.matchday.unpick(map)
