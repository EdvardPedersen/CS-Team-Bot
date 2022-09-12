from pytube import Playlist
from dadjokes import Dadjoke
from generic_message_handler import GenericMessageHandler
import random


class StupidityHandler(GenericMessageHandler):
    def __init__(self, help_text, response, reply_private, log_level):
        super().__init__(help_text, response, reply_private, log_level)

    def dad_jokes(self):
        ''' Returns a random dad joke '''
        msg = Dadjoke().joke
        return(msg)

    async def message_dad(self, message, permission):
        await self.reply(message, self.dad_jokes())

    def dank(self):
        ''' Returns a random dank video from a playlist on youtube '''
        playlist = Playlist(
            'https://www.youtube.com/watch?v=q6EoRBvdVPQ&list=PLFsQleAWXsj_4yDeebiIADdH5FMayBiJo')
        yt = random.choice(playlist.videos)
        return(f"https://www.youtube.com/watch?v={yt.video_id}&list=PLFsQleAWXsj_4yDeebiIADdH5FMayBiJo")

    async def message_dank(self, message, permission):
        await self.reply(message, self.dank())
