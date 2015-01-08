from pushbullet import PushBullet
from heartbeat.notifications import Notifier
from heartbeat.platform import Configuration
from datetime import datetime


class pushbullet(Notifier):

    __slots__ = ('api_key', 'message', 'title', 'api_keys')

    def __init__(self):
        config = Configuration()
        self.api_keys = config.config['heartbeat.notifiers.pushbullet']['api_keys']
        super(pushbullet, self).__init__()

    def load(self, event):
        host = event.host
        self.title = event.title + ": " + host
        date = datetime.now()
        self.message = host + ": " + event.message + " at " + \
            event.timestamp.strftime("%H:%M:%S %m/%d/%y")

    def run(self):
        for key in self.api_keys:
            pb = PushBullet(key)
            success, push = pb.push_note(self.title, self.message)
