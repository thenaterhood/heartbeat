from heartbeat.notifications import Notifier
from datetime import datetime
from heartbeat.network import NetworkInfo
import urllib.parse
import urllib.request

net = NetworkInfo()
community_name = net.ip_wan


class dweet(Notifier):
    """
    @deprecated: use heartbeat.pluggable.dweetio.Dweet
    """
    __slots__ = ('message', 'title', 'host')

    def __init__(self):
        super(dweet, self).__init__()

    def load(self, event):
        host = event.host
        self.host = event.host
        self.title = event.title + ": " + host
        date = datetime.now()
        self.message = host + ": " + event.message + " at " + \
            event.timestamp.strftime("%H:%M:%S %m/%d/%y")

    def run(self):
        # Push a notification to wherever
        payload = {'title': self.title, 'message': self.message}
        payload_url = urllib.parse.urlencode(payload)
        name = community_name + '.' + self.host

        try:
            full_url = 'https://dweet.io/dweet/for/' + name + '?' + payload_url
            urllib.request.urlopen(full_url, timeout=5)

        except:
            pass
