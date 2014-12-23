from heartbeat.monitoring import Monitor
from heartbeat.platform import Event
from heartbeat.network import NetworkInfo


class LANIp(Monitor):

    def __init__(self, callback):
        super(LANIp, self).__init__(callback)
        self.ipv4 = '0.0.0.0'

    def run(self):
        net = NetworkInfo()
        if (net.ip_lan != self.ipv4):
            self.ipv4 = net.ip_lan
            event = Event(
                "New LAN IP", "LAN IP address is now " + net.ip_lan, net.fqdn)
            event.one_time = True
            event.payload['ip'] = self.ipv4
            event.payload['ip_type'] = 'LAN'

            self.callback(event)

class WANIp(Monitor):

    def __init__(self, callback):
        super(WANIp, self).__init__(callback)
        self.ipv4 = '0.0.0.0'

    def run(self):
        net = NetworkInfo()
        if (net.ip_wan != self.ipv4):
            self.ipv4 = net.ip_wan
            event = Event(
                "New WAN IP", "WAN IP address is now " + net.ip_wan, net.fqdn)
            event.one_time = True
            event.payload['ip'] = self.ipv4
            event.payload['ip_type'] = 'WAN'

            self.callback(event)
