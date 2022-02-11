import re
import datetime

class Registration():
    def __init__(self,users,date=None) -> None:
        self.date = None
        self.playdate_next(date)
        self.players = users
        self.status = False

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
        self.status = True

    def set_passive(self):
        self.status = False

class RegistrationManager:
    def __init__(self):
        self.registration_active = False
        self.next_match = None
        self.registration_next = None
        self.registration_post = None
        self.my_regex = re.compile("^!registration")

    def method(self, message):
        if my_regex.match(message.content):
            pass
