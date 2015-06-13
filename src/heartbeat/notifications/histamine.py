from heartbeat.notifications import Notifier
from datetime import datetime
from heartbeat.platform import get_config_manager
from heartbeat.network import SocketBroadcaster
from heartbeat.security import Encryptor


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
        settings = get_config_manager()
        broadcaster = SocketBroadcaster(22000, settings.heartbeat.monitor_server)
        data = settings.heartbeat.secret_key
        if (settings.use_encryption):
            encryptor = Encryptor(settings.enc_password)
            data += encryptor.encrypt(self.event.to_json())
        else:
            data += self.event.to_json()

        broadcaster.push(bytes(data.encode("UTF-8")))
