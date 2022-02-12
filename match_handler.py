import re
import datetime
from generic_message_handler import GenericMessageHandler
from constants import Permissions


class Match():
    def __init__(self,users,date=None) -> None:
        self.date = None
        self.playdate_next(date)
        self.players = users
        self.status = "active"

    def playdate_next(self,date):
        if date:
            self.date = date
        else:
            playday = "Wednesday"
            weekdays = {
                'Monday':0,
                'Tuesday':1,
                'Wednesday':2,
                'Thursday':3,
                'Friday':4,
                'Saturday':5,
                'Sunday':6,
            }
            days_in_week = len(weekdays.keys())
            today = datetime.date.today()
            days_to = weekdays[playday] - datetime.date.weekday(today)
            if days_to <= 0: # we are past playday this week
                days_to += days_in_week
            self.date =  today + datetime.timedelta(days_to)

    def set_active(self):
        self.status = "active"

    def set_passive(self):
        self.status = "inactive"

class RegistrationHandler(GenericMessageHandler):
    def __init__(self,commands,help_text,response,reply_private,permission=Permissions.admin):
        super().__init__(commands,help_text,response,reply_private,permission)
        self.registration_active = False
        self.next_match = None
        self.registration_next = None
        self.registration_post = None
        self.setup_handlers()

    async def register(self,message):
        await self.reply(message,"Registration not implemented")
    
    async def cancel(self, message):
        await self.reply(message,"Cancelation not implements")
    
    async def end(self, message):
        await self.reply(message,"End not implemented")

    async def method(self, message,permissions):
        if not self.match_regex(message.content):
            return
        if permissions < self.permissionRequired:
            return

        await self.handler(message)
