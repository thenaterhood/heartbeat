from heartbeat.notifiers import NotifyWorker
from datetime import datetime
import heartbeat.settings
from heartbeat.network import SocketBroadcaster

PORT = 22000

class Histamine(NotifyWorker):
    """
    Calls up and sends hardware events to a monitoring server
    """

    __slots__ = ('message', 'title')

    def __init__(self, event):
        host = event.host
        self.title = event.title + ": " + host
        date = datetime.now()
        self.message = host + ": " + event.message + " at " + event.timestamp.strftime("%H:%M:%S %m/%d/%y")
        super(Histamine, self).__init__(event)

    def run(self):
        broadcaster = SocketBroadcaster(PORT)
        data = heartbeat.settings.SECRET_KEY + self.event.to_json()
        broadcaster.push(bytes(data.encode("UTF-8")))
