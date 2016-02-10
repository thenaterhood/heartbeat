"""
Heartbeat plugin for interacting with the dweet.io service.
This plugin will send dweets for events received from heartbeat.

This module does not have any configurable options.
"""

from heartbeat.network import NetworkInfo
from heartbeat.plugin import Plugin
from heartbeat.platform import Topics
import urllib.parse
import urllib.request


class Dweet(Plugin):

    """
    Class that sends a single public dweet
    """

    __slots__ = ('community_name', 'local_hostname')

    def __init__(self):

        net = NetworkInfo()
        self.community_name = net.ip_wan
        self.local_hostname = net.hostname

        super(Dweet, self).__init__()

    def get_subscriptions(self):
        """
        Overrides Plugin.get_subscriptions
        """

        subs = {
            Topics.INFO: self._push_dweet,
            Topics.WARNING: self._push_dweet,
            Topics.DEBUG: self._push_dweet,
            Topics.STARTUP: self._push_dweet
            }

        return subs

    def _push_dweet(self, event):
        """
        Pushes a public dweet to dweet.io
        """
        payload = {
                'title': event.title + ": " + event.host,
                'message': event.host + ": " + event.message + " at " + \
                        event.timestamp.strftime("%H:%M:%S %m/%d/%y")
                }
        payload_url = urllib.parse.urlencode(payload)
        name = self.community_name + "." + self.local_hostname

        try:
            full_url = 'https://dweet.io/dweet/for/' + name + '?' + payload_url
            urllib.request.urlopen(full_url, timeout=5)
        except Exception:
            pass
