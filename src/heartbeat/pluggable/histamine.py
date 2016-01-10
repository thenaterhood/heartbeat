"""
Heartbeat plugins pertaining to Heartbeat's
Histamine system which allows events to be
sent over and received from the network.

Configuration, where applicable, is defined
in the Plugin it pertains to.
"""

from heartbeat.plugin import Plugin
from datetime import datetime
from heartbeat.platform import get_config_manager, Topics
from heartbeat.network import SocketBroadcaster
from heartbeat.security import Encryptor


class Sender(Plugin):

    """
    Calls up and sends hardware events to a monitoring server
    """

    __slots__ = ('monitor_server', 'secret_key', 'use_encryption'
            'enc_password')

    def __init__(self):

        settings = get_config_manager()
        self.monitor_server = settings.heartbeat.monitor_server
        self.secret_key = settings.heartbeat.secret_key
        self.use_encryption = settings.use_encryption
        self.enc_password = settings.heartbeat.enc_password

        super(Sender, self).__init__()

    def get_subscriptions(self):
        """
        Overrides Plugin.get_subcriptions
        """

        subs = {
            Topics.INFO: self.send_event,
            Topics.WARNING: self.send_event,
            Topics.DEBUG: self.send_event,
            Topics.VIRTUAL: self.send_event
            }

        return subs

    def send_event(self, event):
        """
        Sends an event
        """

        broadcaster = SocketBroadcaster(
                22000, self.monitor_server)
        data = self.secret_key
        if (self.use_encryption):
            encryptor = Encryptor(self.enc_password)
            data += encryptor.encrypt(event.to_json())
        else:
            data += event.to_json()

        broadcaster.push(bytes(data.encode("UTF-8")))

