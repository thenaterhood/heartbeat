"""
Heartbeat plugins that monitor various network
information.
"""

from heartbeat.plugin import Plugin
from heartbeat.monitoring import MonitorType
from heartbeat.platform import Event, Topics
from heartbeat.network import NetworkInfo


class LANIp(Plugin):

    """
    Keeps tabs on the LAN IP address
    """

    def __init__(self):
        super(LANIp, self).__init__()
        self.ipv4 = '0.0.0.0'

    def get_producers(self):
        """
        Overrides Plugin.get_producers
        """

        prods = {
            MonitorType.PERIODIC: self.check_ip
            }

        return prods

    def check_ip(self, callback):
        """
        Checks the IP and calls back if it has
        changed since the previous
        """

        net = NetworkInfo()
        if (net.ip_lan != "0.0.0.0" and net.ip_lan != self.ipv4):
            self.ipv4 = net.ip_lan
            event = Event(
                "New LAN IP", "LAN IP address is now " + net.ip_lan, net.fqdn)
            event.one_time = True
            event.payload['ip'] = self.ipv4
            event.payload['ip_type'] = 'LAN'
            event.type = Topics.INFO

            callback(event)


class WANIp(Plugin):

    """
    Keeps tabs on the WAN IP address
    """

    def __init__(self):
        super(WANIp, self).__init__()
        self.ipv4 = '0.0.0.0'

    def get_producers(self):
        """
        Overrides Plugin.get_producers
        """

        prods = {
            MonitorType.PERIODIC: self.check_ip
            }
        return prods

    def check_ip(self, callback):
        """
        Checks the WAN IP and calls back
        if it has changed
        """

        net = NetworkInfo()
        if (net.ip_wan != '0.0.0.0' and net.ip_wan != self.ipv4):
            self.ipv4 = net.ip_wan
            event = Event(
                "New WAN IP", "WAN IP address is now " + net.ip_wan, net.fqdn)
            event.one_time = True
            event.payload['ip'] = self.ipv4
            event.payload['ip_type'] = 'WAN'
            event.type = Topics.INFO

            callback(event)
