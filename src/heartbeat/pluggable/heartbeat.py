"""
Heartbeat's Heartbeat plugins
"""

import datetime
import operator
from time import sleep, time
from random import randint
from heartbeat.network import SocketListener, NetworkInfo
from heartbeat.platform import get_config_manager, Event, Topics
from heartbeat.multiprocessing import BackgroundTimer, Cache
from heartbeat.plugin import Plugin
from heartbeat.monitoring import MonitorType
from heartbeat.network import SocketBroadcaster


class Startup(Plugin):

    """
    Sends an event when heartbeat starts
    """

    def __init__(self, netinfo=None):
        """
        Constructor

        Params:
            Settings settings
        """
        if netinfo is None:
            netinfo = NetworkInfo()

        self.fqdn = netinfo.get_hostname()

        super(Startup, self).__init__()

    def get_producers(self):
        """
        Overrides Plugin.get_producers
        """
        prods = {
            MonitorType.REALTIME: self.run
            }

        return prods

    def run(self, callback):
        """
        Run method. Runs a single time then
        exits as this monitor doesn't need to
        run persistently.
        """
        e = Event(
                title="Startup Notification",
                message="Heartbeat has started",
                host=self.fqdn,
                type=Topics.STARTUP
                )
        callback(e)


class Pulse(Plugin):

    """
    Produces a network heartbeat (Event-powered)
    which other systems can monitor
    """

    def __init__(self, timer=None, netinfo=None, settings=None, bcaster=None):
        """
        Constructor

        Params:
            BackgroundTimer timer (optional)
        """
        self.bcaster = bcaster

        if timer is None:
            timer = BackgroundTimer(20*randint(1,5), True, self._beat)

        self.timer = timer

        if netinfo is None:
            netinfo = NetworkInfo()

        self.settings = settings

        self.fqdn = netinfo.get_fqdn()
        self.callback = None

    def get_producers(self):
        """
        Overrides Plugin.get_producers
        """

        prods = {
            MonitorType.REALTIME: self.run
            }

        return prods

    def get_required_services(self):
        """ Overrides Plugin.get_required_services """
        return ['5be95170-2279-4db4-9c07-862ad3c9dfb3']

    def halt(self):
        """ Terminates the heartbeat """
        self.timer.stop()

    def _beat(self):
        """ Sends a heartbeat """
        e = Event(
                title="System heartbeat",
                message="",
                type=Topics.HEARTBEAT,
                host=self.fqdn
            )

        if self.callback is not None:
            self.callback(e)

    def _legacy_beat(self):

        data = self.settings.heartbeat.secret_key.encode("UTF-8") + self.fqdn.encode("UTF-8")
        self.bcaster.push(data)

    def run(self, callback):
        """ Starts the heartbeat """

        self.callback = callback
        self.timer.start()


class PulseMonitor(Plugin):

    """
    A monitor class to listen for and handle the known heartbeats on the
    network.

    This class is Event-driven and will ignore heartbeats on the legacy
    (non-event) system. This class listens to Pulses.
    """

    def __init__(self, cache=None):
        """
        constructor

        Params:
            Cache cache (optional)
        """
        if cache is None:
            self.cache = Cache('known-pulses')
        else:
            self.cache = cache

        self.cache.resetValuesTo(time())
        self.shutdown = False

        super(PulseMonitor, self).__init__()

        self.realtime = True

    def get_subscriptions(self):
        """ Overrides Plugin.get_subscriptions """
        subs = {
                Topics.HEARTBEAT: self.receive
            }

        return subs

    def get_producers(self):
        """
        Overrides Plugin.get_producers
        """

        prods = {
                MonitorType.PERIODIC: self.cleanup_hosts,
                # There's a limitation where we'll only be given a callback
                # we can keep for a realtime monitor. This is just a method
                # to capture the callback, since PulseMonitor doesn't
                # need to run continuously.
                MonitorType.REALTIME: self.set_callback
            }

        return prods

    def set_callback(self, callback):
        # There's a limitation where we'll only be given a callback
        # we can keep for a realtime monitor. This is just a method
        # to capture the callback, since PulseMonitor doesn't
        # need to run continuously.
        self.callback = callback

    def get_required_services(self):
        """ Overrides Plugin.get_required_services """
        return ['dbb651d2-bce4-466b-9c01-2c5df2ead863']

    def halt(self):
        """
        Shuts down the thread cleanly
        """
        self.shutdown = True
        self.saveCache()

    def saveCache(self):
        """
        Saves the cache out to disk
        """
        self.cache.writeToDisk()

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

    def receive(self, event):
        """
        Receives a heartbeat event
        """
        if not self._bcastIsOwn(event.host):
            self._log_host(event.host)

    def receive_legacy(self, data, addr):
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
        if (host not in self.cache.keys()):
            event = Event("New Heartbeat", "New heartbeat discovered", host)
            self.callback(event)

        self.cache.write(host, time())

    def cleanup_hosts(self, callback):
        """
        Cleans up the known heartbeats and notifies of any that haven't
        been heard for a while, then dumps them.
        """
        logged_hosts = self.cache.items()
        remove_hosts = []

        for host, logged_time in logged_hosts:
            difference = datetime.datetime.now() - datetime.datetime.fromtimestamp(logged_time)

            if difference > datetime.timedelta(seconds=300):
                event = Event(
                    "Flatlined Host",
                    "Host flatlined (heartbeat lost)",
                    host,
                )

                callback(event)
                remove_hosts.append(host)

        for host in remove_hosts:
            self.cache.remove(host)

        self.saveCache()


class Heartbeat(Pulse):

    """
    Defines a heartbeat thread which will send a broadcast
    over the network every given interval (plus a small random margin
    so as to avoid flooding the network)
    """

    def __init__(self, bcaster=None, timer=None, settings=None):
        """
        constructor
        """
        timer = BackgroundTimer(20*randint(1,5), True, self._legacy_beat)

        if settings is None:
            settings = get_config_manager()

        if bcaster is None:
            bcaster = SocketBroadcaster(
                settings.heartbeat.port,
                settings.heartbeat.monitor_server
            )


        super(Heartbeat, self).__init__(timer, bcaster=bcaster, settings=settings)

    def get_required_services(self):
        return []


class Monitor(PulseMonitor):

    """
    A monitor class to listen for and handle the known heartbeats on the
    network.
    """

    def __init__(self, cache=None, settings=None, listener=None):
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
        if settings is None:
            settings = get_config_manager()
        else:
            settings = settings
        secret = settings.heartbeat.secret_key

        self.port = settings.heartbeat.port
        self.secret = bytes(secret.encode("UTF-8"))

        if listener is None:
            self.listener = SocketListener(self.port, self.receive_legacy)
        else:
            self.listener = listener

        super(Monitor, self).__init__(cache=cache)

    def get_producers(self):
        """
        Overrides Plugin.get_producers
        """

        prods = {
                MonitorType.REALTIME: self.run_legacy,
                MonitorType.PERIODIC: self.cleanup_hosts
            }

        return prods

    def get_required_services(self):
        return []

    def run_legacy(self, callback):
        """
        Runs the monitor. Usually called by the parent start()
        """
        self.listener.start()
        self.callback = callback

        while not self.shutdown:
            sleep(5)
