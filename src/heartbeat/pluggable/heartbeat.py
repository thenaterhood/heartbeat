"""
Heartbeat's Heartbeat plugins
"""

import threading
import os
import datetime
import operator
from time import sleep
from random import randint
from heartbeat.network import SocketListener, NetworkInfo
from heartbeat.platform import get_config_manager, Event
from heartbeat.multiprocessing import LockingDictionary, BackgroundTimer
from heartbeat.security import Encryptor
from heartbeat.plugin import Plugin
from heartbeat.monitoring import MonitorType
from heartbeat.network import SocketBroadcaster


class Heartbeat(Plugin):

    """
    Defines a heartbeat thread which will send a broadcast
    over the network every given interval (plus a small random margin
    so as to avoid flooding the network)
    """

    def __init__(self, bcaster=None, timer=None):
        """
        constructor

        Params:
            int    port:     the port number to broadcast on
            int    interval: the base interval to use for beats
            string secret:   a secret string to identify the heartbeat
        """
        settings = get_config_manager()
        self.secret = bytes(settings.heartbeat.secret_key.encode("UTF-8"))

        self.bcaster = bcaster
        if (bcaster is None):
            self.bcaster = SocketBroadcaster(
                settings.heartbeat.port,
                settings.heartbeat.monitor_server
            )

        self.timer = timer
        if (timer is None):
            self.timer = BackgroundTimer(5*randint(1,5), True, self._beat)

        super(Heartbeat, self).__init__()

    def get_producers(self):
        """
        Overrides Plugin.get_producers
        """

        prods = {
            MonitorType.REALTIME: self.start
        }

        return prods

    def terminate(self):
        """
        Shuts down the thread cleanly
        """
        self.timer.stop()

    def _beat(self):
        """
        Broadcasts a single beat
        """
        netinfo = NetworkInfo()
        data = self.secret + bytes(netinfo.fqdn.encode("UTF-8"))
        self.bcaster.push(data)

    def start(self, callback):
        """
        Runs the heartbeat (typically started by the thread start() call)
        """
        self.callback = callback
        self.timer.start()


class Monitor(Plugin):

    """
    A monitor class to listen for and handle the known heartbeats on the
    network.
    """

    def __init__(self):
        """
        constructor

        Params:
            int port: the port to listen on. Must match that of the heartbeats
               this is intended to watch
            string secret: a secret string to identify the heartbeat. Must
               match that of the heartbeats this is intended to watch
            NotificationHandler notifyHandler: an array of notifier classes to call to send
                notifications of events
        """
        settings = get_config_manager()
        secret = settings.heartbeat.secret_key

        self.port = settings.heartbeat.port
        self.known_hosts = []
        self.secret = bytes(secret.encode("UTF-8"))
        self.listener = SocketListener(self.port, self.receive)
        self.cachefile = settings.heartbeat.cache_dir + "/heartbeats"
        self.shutdown = False

        super(Monitor, self).__init__()

        self.realtime = True

    def get_producers(self):
        """
        Overrides Plugin.get_producers
        """

        prods = {
                MonitorType.REALTIME: self.run,
                MonitorType.PERIODIC: self.cleanup_hosts
            }

        return prods

    def terminate(self):
        """
        Shuts down the thread cleanly
        """
        self.listener.shutdown = True
        self.saveCache()

    def saveCache(self):
        """
        Saves the cache out to disk
        """
        hosts = self.known_hosts.keys()
        try:
            fileHandle = open(self.cachefile, 'w')
            for h in hosts:
                fileHandle.write(h + "\n")
            fileHandle.close()
        except Exception:
            pass

    def loadCache(self):
        """
        Loads the cache from file
        """
        if (os.path.isfile(self.cachefile)):
            for h in open(self.cachefile, 'r'):
                self.known_hosts.write(h.strip(), datetime.datetime.now())

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
        if data.startswith(self.secret) and not self._bcastIsOwn(data[len(self.secret):].decode("UTF-8")):
            host = data[len(self.secret):].decode("UTF-8")
            self._log_host(host)

    def _log_host(self, host):
        """
        Notifies of and adds a newly discovered heartbeat on the network

        Params:
            string host: the host the broadcast originated from
        """
        if (host not in self.known_hosts.keys()):
            event = Event("New Heartbeat", "New heartbeat discovered", host)
            self.callback(event)

        self.known_hosts.write(host, datetime.datetime.now())

    def cleanup_hosts(self, callback):
        """
        Cleans up the known heartbeats and notifies of any that haven't
        been heard for a while, then dumps them.
        """
        sorted_hosts = sorted(
            self.known_hosts.items(), key=operator.itemgetter(1))
        i = 0
        while (i < len(sorted_hosts) and datetime.datetime.now() - sorted_hosts[i][1] > datetime.timedelta(seconds=90)):
            event = Event(
                "Flatlined Host", "Host flatlined (heartbeat lost)", sorted_hosts[i][0])
            callback(event)
            self.known_hosts.remove(sorted_hosts[i][0])
            i += 1

        self.saveCache()

    def run(self, callback):
        """
        Runs the monitor. Usually called by the parent start()
        """
        self.known_hosts = LockingDictionary()
        self.loadCache()
        self.listener.start()
        self.callback = callback

        while not self.shutdown:
            sleep(10)

        self.terminate()
