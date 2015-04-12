from heartbeat.notifications import Notifier
from datetime import datetime
from heartbeat.platform import Configuration
from heartbeat.network import SocketBroadcaster

PORT = 22000


class Histamine(Notifier):

    """
    Calls up and sends hardware events to a monitoring server
    """

    __slots__ = ('message', 'title')

    def __init__(self):
        super(Histamine, self).__init__()

    def load(self, event):
        self.event = event
        host = event.host
        self.title = event.title + ": " + host
        date = datetime.now()
        self.message = host + ": " + event.message + " at " + \
            event.timestamp.strftime("%H:%M:%S %m/%d/%y")

    def run(self):
        settings = Configuration()
        broadcaster = SocketBroadcaster(PORT, settings.config['monitor_server'])
        data = settings.config['secret_key'] + self.event.to_json()
        broadcaster.push(bytes(data.encode("UTF-8")))
