from heartbeat.notifications import Notifier
from datetime import datetime


class NotifyTemplate(Notifier):

    __slots__ = ('message', 'title')

    def __init__(self):
        super(NotifyTemplate, self).__init__()

    def load(self, event):
        host = event.host
        self.title = event.title + ": " + host
        date = datetime.now()
        self.message = host + ": " + event.message + " at " + \
            event.timestamp.strftime("%H:%M:%S %m/%d/%y")

    def run(self):
        # Push a notification to wherever
        pass
