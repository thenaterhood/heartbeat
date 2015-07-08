from heartbeat.notifications import Notifier
from datetime import datetime


class NotifyTemplate(Notifier):

    __slots__ = ('message', 'title')

    def __init__(self):
        super(NotifyTemplate, self).__init__()

    def run(self):
        # Push a notification to wherever
        pass
