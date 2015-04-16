from heartbeat.notifications import Notifier
from heartbeat.platform import get_config_manager
import urllib.parse
import urllib.request


class UrlPull(Notifier):

    __slots__ = ('current_ip', 'new_ip', 'url')

    def __init__(self):
        self.current_ip = None
        self.new_ip = None
        config = get_config_manager()
        self.url = config.notifying.dyndns.urlpull
        super(UrlPull, self).__init__()

    def load(self, event):

        if ('ip_type' in event.payload
                and event.payload['ip_type'] == 'WAN'
                ):
            ip = event.payload['ip']
            if (ip != self.current_ip):
                self.new_ip = ip

    def run(self):

        try:
            if (self.new_ip != None):
                urllib.request.urlopen(self.url, timeout=5)
                self.current_ip = self.new_ip
                self.new_ip = None
            else:
                pass
        except:
            pass
