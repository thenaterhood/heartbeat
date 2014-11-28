from heartbeat.notifiers import NotifyWorker
from datetime import datetime


class PrintOutput(NotifyWorker):

    __slots__ = ('message', 'title')

    def __init__(self, event):
        host = event.host
        self.title = event.title + ": " + host
        date = datetime.now()
        self.message = host + ": " + event.message + " at " + \
            event.timestamp.strftime("%H:%M:%S %m/%d/%y")
        super(PrintOutput, self).__init__(event)

    def run(self):
        # Push a notification to wherever
        print(self.title + ": " + self.message)
