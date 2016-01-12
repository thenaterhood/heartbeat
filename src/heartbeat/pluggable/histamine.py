"""
Heartbeat plugins pertaining to Heartbeat's
Histamine system which allows events to be
sent over and received from the network.

Configuration, where applicable, is defined
in the Plugin it pertains to.
"""

from heartbeat.plugin import Plugin
from datetime import datetime
from heartbeat.platform import get_config_manager, Topics, Event
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
        self.use_encryption = settings.heartbeat.use_encryption
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


class Listener(Plugin):

    """
    A monitor class to listen for and handle events received from devices
    using the HeartbeatServer monitor.
    """

    def __init__(self):
        """
        constructor

        Params:
            int port: the port to listen on. Must match that of the heartbeats
               this is intended to watch
            string secret: a secret string to identify the heartbeat. Must
               match that of the heartbeats this is intended to watch
            Notificationhandler notifyHandler: notification handler
        """
        self.settings = get_config_manager()
        secret = self.settings.heartbeat.secret_key

        self.callback = callback
        self.secret = bytes(secret.encode("UTF-8"))
        self.listener = SocketListener(22000, self.receive)

        super(Listener, self).__init__()
        self.realtime = True
        self.shutdown = False

    def get_producers(self):
        """
        Overrides Plugin.get_producers
        """

        prods = {
            MonitorType.REALTIME: self.run
            }

        return prods

    def _bcastIsOwn(self, host):
        """
        Determines if a received broadcast is from the same machine

        Params:
            string host: the host the broadcast originated from (fqdn)
        Returns:
            boolean: whether the broadcast originated from ourselves
        """
        netinfo = NetworkInfo()
        return host == netinfo.fqdn

    def receive(self, data, addr):
        """
        Receives the data and address from a broadcast. Used for the
        SocketListener to call back to when it receives something.

        Params:
            binary data: the undecoded data from the broadcast
            binary addr:
        """
        if data.startswith(self.secret):
            eventJson = data[len(self.secret):].decode("UTF-8")
            event = Event.from_json(eventJson)

            event_loaded = False

            if (self._bcastIsOwn(event.host)):
                return

            if (self.settings.accept_plaintext or not self.settings.use_encryption):
                try:
                    event = Event.from_json(eventJson)
                    event_loaded = True
                except:
                    pass

            if (not event_loaded and self.settings.use_encryption):
                try:
                    encryptor = Encryptor(self.settings.enc_password)
                    event = Event.from_json(encryptor.decrypt(eventJson))
                    event_loaded = True
                except:
                    pass

            if (event_loaded):
                self.callback(event)

    def terminate(self):
        """
        Shuts down the thread cleanly
        """
        self.listener.shutdown = True

    def run(self, callback):
        """
        Runs the monitor. Usually called by the parent start()
        """
        self.callback = callback
        self.listener.start()

        while not self.shutdown:
            sleep(4)

        self.terminate()
