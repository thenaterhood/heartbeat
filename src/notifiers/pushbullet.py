from pushbullet import PushBullet
from notifiers import NotifyWorker
from datetime import datetime

API_KEYS = [
    'Xbgeg5x0pSup5OH9lzK9MKcjQ3ughNT1',
]

class pushbullet(NotifyWorker):

    __slots__ = ('api_key', 'message', 'title')

    def __init__(self, event):
        host = event.host
        self.title = event.title + ": " + host
        date = datetime.now()
        self.message = host + ": " + event.message + " at " + event.timestamp.strftime("%H:%M:%S %m/%d/%y")
        super(pushbullet, self).__init__(event)

    def run(self):
        for key in API_KEYS:
            pb = PushBullet(key)
            success, push = pb.push_note(self.title, self.message)

