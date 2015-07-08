from pushbullet import PushBullet
from heartbeat.notifications import Notifier
from heartbeat.platform import get_config_manager
from datetime import datetime


class pushbullet(Notifier):

    __slots__ = ('api_key', 'message', 'title', 'api_keys')

    def __init__(self):
        config = get_config_manager()
        self.api_keys = config.notifying.pushbullet.api_keys
        super(pushbullet, self).__init__()

    def run(self):
        for key in self.api_keys:
            pb = PushBullet(key)
            success, push = pb.push_note(self.title, self.message)
