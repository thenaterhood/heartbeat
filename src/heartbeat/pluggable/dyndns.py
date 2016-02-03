"""
This is a collection of heartbeat plugins.

This module contains plugins for interacting
with dynamic DNS systems. Configuration of
each plugin is in the plugin's class.
"""

from heartbeat.platform import get_config_manager, Topics
from heartbeat.plugin import Plugin
import urllib.parse
import urllib.request


class UrlPull(Plugin):

    """
    Pulls a URL on a new WAN IP address

    This plugin can be configured by adding
    a section to the notifying.conf file in
    /etc/heartbeat/ (or the appropriate location
    for your install) as follows:

    dyndns:
        urlpull: URL_TO_REQUEST
    """

    __slots__ = ('current_ip', 'new_ip', 'url')

    def __init__(self):
        self.current_ip = None
        self.new_ip = None
        config = get_config_manager()
        self.url = config.notifying.dyndns.urlpull

        super(UrlPull, self).__init__()

    def get_subscriptions(self):
        """
        Overrides Plugin.get_subscriptions
        """

        subs = {
            Topics.INFO: self.update_dyndns
            }

        return subs

    def get_required_services(self):
        """
        Overrides Plugin.get_required_services
        """
        return ['f21fc976-d53d-462f-a90f-38e2c564e989']

    def update_dyndns(self, event):
        if ('ip_type' in event.payload and event.payload['ip_type'] == 'WAN'):

            ip = event.payload['ip']
            if ip != self.current_ip or self.current_ip is None:
                try:
                    urllib.request.urlopen(self.url, timeout=5)
                    self.current_ip = ip
                except Exception:
                    pass

