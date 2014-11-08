from notifiers import NotifyWorker
from datetime import datetime

class NotifyTemplate(NotifyWorker):

    __slots__ = ('message', 'title')

    def __init__(self, event):
        host = event.host
        self.title = event.title + ": " + host
        date = datetime.now()
        self.message = host + ": " + event.message + " at " + event.timestamp.strftime("%H:%M:%S %m/%d/%y")
        super(NotifyTemplate, self).__init__(event)

    def run(self):
        # Push a notification to wherever
        pass
