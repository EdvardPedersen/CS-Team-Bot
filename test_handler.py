import random
import logging
import re
from generic_message_handler import GenericMessageHandler
from helper_functions import admin_check, infinite_sequence_gen
from  match import MatchDay
from player import Player

'''
Publicly available tests, callable from the discord client
Admin only
'''

def log(function):
    async def inner(self,message):
        self.log.info(f"{message.author} running: {function.__name__}")
        await function(self,message)
        self.log.info("Ok")

    return inner

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

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

# first file logger
logger = setup_logger('first_logger', 'first_logfile.log')
logger.info('This is just info message')

# second file logger
super_logger = setup_logger('second_logger', 'second_logfile.log')
super_logger.error('This is an error message')

def another_method():
   # using logger defined above also works here
   logger.info('Inside method')
class TestHandler(GenericMessageHandler):
    def __init__(self, help_text, response, reply_private):
        super().__init__(help_text, response, reply_private)
        self.log = setup_logger(self.__class__.__name__,f"{self.__class__.__name__}.log",logging.DEBUG)

    @admin_check
    @log
    async def message_test_banorder(self,message):
        num_matches = 2
        num_players = 8
        id_gen = infinite_sequence_gen()
        players =  {}
        for i in  range(num_players):
            players[i] = Player.generate_random(next(id_gen))

        matchday =  MatchDay({})
        for player in  players.values():
            matchday.player_add(player)
        matchday.set_message(TestMessage())
        matchday.set_banorder_message(TestMessage())
        
        self.log.debug(matchday.registration_start(f"!register {num_matches}"))
        self.log.debug(await matchday.registration_end(players))
        self.log.debug([player.id for player in players.values()])
        for team in  matchday.teams.values():
            self.log.debug(team.get_info())
        self.log.debug(matchday.banorder())
        self.log.debug("Veto:(As home team)\n")
        for i in  range(6):
            #ban ban ban  pick  pick
            if i<4: # ban
                if  not i%2:
                    map = matchday.get_next_ban()
                    self.log.debug(f"Banning by preference: {map}")
                    await matchday.ban(map)
                else:
                    map = random.choice(matchday.available_maps)
                    self.log.debug(f"Banning random: {map}")
                    await matchday.ban(map)
            else: # pick
                if i%2:
                    map = matchday.get_next_pick()
                    self.log.debug(f"Picking by  preference: {map}")
                    await matchday.pick(map)
                else:
                    map = random.choice(matchday.available_maps)
                    self.log.debug(f"Picking random: {map}")
                    await matchday.pick(map)
            self.log.debug(matchday.banorder())

        log = f"\n~~Veto Result~~\n"
        log += f"{matchday.banorder()}"
        await self.reply(message,log)