from pushbullet import PushBullet
from heartbeat.notifiers import NotifyWorker
from heartbeat.settings import Configuration
from datetime import datetime


class pushbullet(NotifyWorker):

    __slots__ = ('api_key', 'message', 'title', 'api_keys')

    def __init__(self, event):
        config = Configuration()
        self.api_keys = config.config['heartbeat.notifiers.pushbullet']['api_keys']
        host = event.host
        self.title = event.title + ": " + host
        date = datetime.now()
        self.message = host + ": " + event.message + " at " + \
            event.timestamp.strftime("%H:%M:%S %m/%d/%y")
        super(pushbullet, self).__init__(event)

    def run(self):
        for key in self.api_keys:
            pb = PushBullet(key)
            success, push = pb.push_note(self.title, self.message)
