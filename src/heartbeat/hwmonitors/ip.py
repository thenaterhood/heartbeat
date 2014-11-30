from heartbeat.hwmonitors import MonitorWorker
from heartbeat.notifiers import Event
from heartbeat.network import NetworkInfo


class LANIp(MonitorWorker):

    def __init__(self, callback):
        super(LANIp, self).__init__(callback)

    def run(self):
        net = NetworkInfo()

        event = Event(
            "New LAN IP", "LAN IP address is now " + net.ip_lan, net.fqdn)
        event.one_time = True

        self.callback(event)


class WANIp(MonitorWorker):

    def __init__(self, callback):
        super(WANIp, self).__init__(callback)

    def run(self):
        net = NetworkInfo()
        event = Event(
            "New WAN IP", "WAN IP address is now " + net.ip_wan, net.fqdn)
        event.one_time = True

        self.callback(event)
