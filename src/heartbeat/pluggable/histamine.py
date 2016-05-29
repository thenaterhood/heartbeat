"""
Heartbeat plugins pertaining to Heartbeat's
Histamine system which allows events to be
sent over and received from the network.

Configuration, where applicable, is defined
in the Plugin it pertains to.
"""

from heartbeat.plugin import Plugin
from heartbeat.platform import get_config_manager, Topics, Event
from heartbeat.network import SocketBroadcaster, SocketListener, NetworkInfo
from heartbeat.security import Encryptor
from heartbeat.monitoring import MonitorType
from time import sleep
import os
import socket


class Sender(Plugin):

    """
    Calls up and sends hardware events to a monitoring server
    """

    __slots__ = ('monitor_server', 'secret_key', 'use_encryption'
            'enc_password')

    def __init__(self):

        settings = get_config_manager()
        self.topics = {}
        self.monitor_server = settings.heartbeat.monitor_server
        self.secret_key = settings.heartbeat.secret_key
        self.use_encryption = settings.heartbeat.use_encryption
        self.enc_password = settings.heartbeat.enc_password

        if "histamine" in settings.notifying and "topics" in settings.notifying.histamine:
            send_topics = settings.notifying.histamine.topics
            for s in send_topics:
                if s.upper() in Topics:
                    self.topics[Topics[s.upper()]] = self.send_event
        else:
            self.topics = {
                Topics.INFO: self.send_event,
                Topics.WARNING: self.send_event,
                Topics.DEBUG: self.send_event,
                Topics.VIRT: self.send_event,
                Topics.HEARTBEAT: self.send_event,
                Topics.STARTUP: self.send_event
                }

        super(Sender, self).__init__()

    def get_subscriptions(self):
        """
        Overrides Plugin.get_subcriptions
        """

        return self.topics

    def get_services(self):
        """ Overrides Plugin.get_services """
        return ['5be95170-2279-4db4-9c07-862ad3c9dfb3']

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
        self.topics = []
        self.settings = get_config_manager()
        secret = self.settings.heartbeat.secret_key

        self.secret = bytes(secret.encode("UTF-8"))
        self.callback = None
        super(Listener, self).__init__()
        self.realtime = True
        self.shutdown = False

        if "histamine" in self.settings.monitoring and "topics" in self.settings.monitoring.histamine:

            recv_topics = self.settings.monitoring.histamine.topics
            for r in recv_topics:
                try:
                    self.topics.append(Topics[r.upper()])
                except KeyError:
                    pass
        else:
            self.topics = [
                Topics.INFO,
                Topics.WARNING,
                Topics.DEBUG,
                Topics.VIRT,
                Topics.HEARTBEAT,
                Topics.STARTUP
                ]

    def get_producers(self):
        """
        Overrides Plugin.get_producers
        """

        prods = {
            MonitorType.REALTIME: self.run
            }

        return prods

    def get_services(self):
        """ Overrides Plugin.get_services """
        return ['dbb651d2-bce4-466b-9c01-2c5df2ead863']

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

            if (self.settings.heartbeat.accept_plaintext or not self.settings.heartbeat.use_encryption):
                try:
                    event = Event.from_json(eventJson)
                    event_loaded = True
                except Exception:
                    pass

            if (not event_loaded and self.settings.heartbeat.use_encryption):
                try:
                    encryptor = Encryptor(self.settings.heartbeat.enc_password)
                    event = Event.from_json(encryptor.decrypt(eventJson))
                    event_loaded = True
                except Exception:
                    pass

            if (event_loaded and event.type in self.topics):
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
        self.listener = SocketListener(22000, self.receive)
        self.listener.start()

        while not self.shutdown:
            sleep(4)

        self.terminate()

class LocalSocket(Listener):

    def __init__(self, settings=None):
        """
        constructor
        """
        super(LocalSocket, self).__init__()

        self.sock_address = "/tmp/heartbeat.sock"
        try:
            os.unlink(self.sock_address)
        except OSError:
            if os.path.exists(self.sock_address):
                raise

        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        self.callback = None
        self.shutdown = False

    def get_producers(self):
        """
        Overrides Plugin.get_producers
        """

        prods = {
            MonitorType.REALTIME: self.run
            }

        return prods

    def get_services(self):
        """ Overrides Plugin.get_services """
        return []

    def halt(self):
        """ Overrides Plugin.halt """
        self.shutdown = True
        self.socket.close()
        os.unlink(self.sock_address)

    def run(self, callback):
        self.socket.bind(self.sock_address)
        self.socket.listen(1)
        self.callback = callback

        while not self.shutdown:
            connection, from_addr = self.socket.accept()
            try:
                data = connection.recv(1024)
                self.receive(data, from_addr)
            except Exception as e:
                # Hope for the best
                pass
            finally:
                connection.close()
