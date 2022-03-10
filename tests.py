import constants
import match
from player import Player
import random


def infinite_sequence():
    num = 0
    while True:
        yield num
        num += 1

class TestChannel():
    def __init__(self, parent) -> None:
        self._parent  = parent
        pass

    def fetch_message(self):
        return self._parent

class TestMessage():
    def  __init__(self) -> None:
        self.reactions = []
        self.channel = TestChannel(self)

    async def pin(self):
        pass
    
    async def unpin(self):
        pass
    
    async def edit(self, content=None):
        pass

async def test_banorder():
    num_matches = 2
    num_players = 8
    id_gen = infinite_sequence()
    players =  {}
    for i in  range(num_players):
        players[i] = Player.generate_random(next(id_gen))

    matchday =  match.MatchDay({})
    for player in  players.values():
        matchday.player_add(player)
    matchday.set_message(TestMessage())
    matchday.set_banorder_message(TestMessage())
    
    print(matchday.registration_start(f"!register {num_matches}"))
    print(await matchday.registration_end(players))
    print([player.id for player in players.values()])
    for team in  matchday.teams.values():
        print(team.get_info())
    print(matchday.banorder())
    print("Veto:(As home team)\n")
    for i in  range(6):
        #ban ban ban  pick  pick
        if i<4: # ban
            if  not i%2:
                map = matchday.get_next_ban()
                print(f"Banning by preference: {map}")
                await matchday.ban(map)
            else:
                map = random.choice(matchday.available_maps)
                print(f"Banning random: {map}")
                await matchday.ban(map)
        else: # pick
            if i%2:
                map = matchday.get_next_pick()
                print(f"Picking by  preference: {map}")
                await matchday.pick(map)
            else:
                map = random.choice(matchday.available_maps)
                print(f"Picking ranom: {map}")
                await matchday.pick(map)
        print(matchday.banorder())

    # log =f"\n~~Veto Result~~\nPicked: {matchday.picked_maps}\nBanned:{matchday.banned_maps}\nAvailable:{matchday.available_maps}\n"
    log = f"\n~~Veto Result~~\n"
    log += f"{matchday.banorder()}"
    return  log