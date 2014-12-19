from time import sleep
import os
import threading
from random import randint
import datetime
import operator
from heartbeat.network import NetworkInfo
from heartbeat.network import SocketListener
from heartbeat.network import SocketBroadcaster
from heartbeat.platform import Event
from heartbeat.multiprocessing import Threadpool


class Heartbeat(threading.Thread):

    """
    Defines a heartbeat thread which will send a broadcast
    over the network every given interval (plus a small random margin
    so as to avoid flooding the network)

    Extends threading.Thread
    """

    def __init__(self, port, interval, secret):
        """
        constructor

        Params:
            int    port:     the port number to broadcast on
            int    interval: the base interval to use for beats
            string secret:   a secret string to identify the heartbeat
        """
        self.port = port
        self.interval = interval
        self.secret = bytes(secret.encode("UTF-8"))
        self.bcaster = SocketBroadcaster(self.port)
        self.shutdown = False

        super().__init__()

    def terminate(self):
        """
        Shuts down the thread cleanly
        """
        pass

    def _beat(self):
        """
        Broadcasts a single beat
        """
        netinfo = NetworkInfo()
        data = self.secret + bytes(netinfo.fqdn.encode("UTF-8"))
        self.bcaster.push(data)

    def run(self):
        """
        Runs the heartbeat (typically started by the thread start() call)
        """
        while not self.shutdown:
            self._beat()
            sleep(5 * randint(1, 5))

        self.terminate()


class HeartMonitor(threading.Thread):

    """
    A monitor class to listen for and handle the known heartbeats on the
    network.
    """

    def __init__(self, port, secret, notifyHandler):
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
        self.port = port
        self.known_hosts = []
        self.secret = bytes(secret.encode("UTF-8"))
        self.notifier = notifyHandler
        self.listener = SocketListener(port, self.receive)
        self.cachefile = '/dev/null'
        self.shutdown = False

        super(HeartMonitor, self).__init__()

    def terminate(self):
        """
        Shuts down the thread cleanly
        """
        self.saveCache()

    def saveCache(self):
        """
        Saves the cache out to disk
        """
        hosts = self.known_hosts.keys()
        fileHandle = open(self.cachefile, 'w')
        for h in hosts:
            fileHandle.write(h)
        fileHandle.close()

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
            self.notifier.push(event)

        self.known_hosts.write(host, datetime.datetime.now())

    def _cleanup_hosts(self):
        """
        Cleans up the known heartbeats and notifies of any that haven't
        been heard for a while, then dumps them.
        """
        sorted_hosts = sorted(
            self.known_hosts.items(), key=operator.itemgetter(1))
        i = 0
        while (i < len(sorted_hosts) and datetime.datetime.now() - sorted_hosts[i][1] > datetime.timedelta(seconds=60)):
            event = Event(
                "Flatlined Host", "Host flatlined (heartbeat lost)", sorted_hosts[i][0])
            self.notifier.receive_event(event)
            self.known_hosts.remove(sorted_hosts[i][0])
            i += 1

        self.saveCache()

    def run(self):
        """
        Runs the monitor. Usually called by the parent start()
        """
        self.known_hosts = LockingDictionary()
        self.loadCache()
        self.listener.start()

        while not self.shutdown:
            sleep(40)
            self._cleanup_hosts()

        self.terminate()


class LockingDictionary():

    """
    A thread-safe wrapper for a dictionary with locking
    """
    __slots__ = ('_semaphore', '_dictionary')

    def __init__(self):
        """
        constructor
        """
        self._dictionary = dict()
        self._semaphore = threading.Semaphore()

    def read(self, key):
        """
        Reads a key from the dictionary

        Params:
            mixed key: the key to return the value of
        """
        return self._dictionary[key]

    def write(self, key, value):
        """
        Adds or updates a key in the dictionary

        Params:
            mixed key: the key to add or update
            mixed value: the value to associate with the key
        """
        self._semaphore.acquire()
        self._dictionary[key] = value
        self._semaphore.release()

    def remove(self, key):
        """
        Deletes a key from the dictionary

        Params:
            mixed key: the key to delete
        """
        self._semaphore.acquire()
        del(self._dictionary[key])
        self._semaphore.release()

    def keys(self):
        """
        Returns a list of the dictionary keys
        """
        return self._dictionary.keys()

    def items(self):
        """
        Returns a list of the dictionary items
        """
        return self._dictionary.items()

    def exists(self, key):
        """
        Returns whether a key is in the dictionary
        """
        return (key in self._dictionary)


class MonitorHandler(threading.Thread):

    """
    Monitoring class handling running multiple monitors on
    an interval
    """

    def __init__(self, hwmonitors, notifyHandler):
        """
        Constructor

        Params:
            array[Monitor] hwmonitors: an array of HardwareWorker
                instances
            NotificationHandler notifyHandler:  notification handler
        """
        self.hwmonitors = []
        self.rtMonitors = []
        realtimeMonitors = 0
        for m in hwmonitors:
            monitor = m(self.receive_event)
            if monitor.realtime:
                realtimeMonitors += 1
                self.rtMonitors.append(monitor)
            else:
                self.hwmonitors.append(monitor)

        self.notifier = notifyHandler
        self.eventTime = LockingDictionary()
        self.eventFrom = LockingDictionary()
        self.shutdown = False
        self.threadpool = Threadpool(5 + realtimeMonitors)
        super(MonitorHandler, self).__init__()

    def run(self):
        """
        Run method, generally called from the parent start()
        """
        for m in self.rtMonitors:
            self.threadpool.add(m.run)

        while not self.shutdown:
            self.scan()
            sleep(60)

        self.terminate()

    def scan(self):
        """
        Runs each monitor thread and waits for it to complete
        """
        for m in self.hwmonitors:
            self.threadpool.add(m.run)

    def terminate(self):
        """
        Shuts down the thread cleanly
        """
        self.threadpool.terminate()

    def notify(self, event):
        self.eventTime.write(event.title, event.timestamp)
        self.eventFrom.write(event.source, event.title)
        self.notifier.receive_event(event)

    def receive_event(self, event):
        """
        A callback method for monitors to call to. Currently just a
        wrapper for the notifier.push
        """
        if (self.eventTime.exists(event.title)):
            lastSeen = self.eventTime.read(event.title)
            delayPassed = (datetime.datetime.now() - lastSeen > datetime.timedelta(hours=2))
            if (not event.one_time and delayPassed):
                self.notify(event)
            else:
                return
        else:
            self.notify(event)


class HistamineNode(threading.Thread):

    """
    A monitor class to listen for and handle events received from devices
    using the HeartbeatServer monitor.
    """

    def __init__(self, port, secret, notifyHandler):
        """
        constructor

        Params:
            int port: the port to listen on. Must match that of the heartbeats
               this is intended to watch
            string secret: a secret string to identify the heartbeat. Must
               match that of the heartbeats this is intended to watch
            Notificationhandler notifyHandler: notification handler
        """
        self.port = port
        self.secret = bytes(secret.encode("UTF-8"))
        self.notifier = notifyHandler
        self.listener = SocketListener(22000, self.receive)
        self.shutdown = False

        super(HistamineNode, self).__init__()

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
            event = Event()
            event.load_json(eventJson)
            if (not self._bcastIsOwn(event.host)):
                self.notifier.receive_event(event)

    def terminate(self):
        """
        Shuts down the thread cleanly
        """
        pass

    def run(self):
        """
        Runs the monitor. Usually called by the parent start()
        """
        self.listener.start()

        while not self.shutdown:
            sleep(40)

        self.terminate()

class NotificationHandler():

    """
    A class that holds a list of notifiers and allows them to
    all be kicked off in succession
    """

    def __init__(self, notifiers):
        """
        Constructor

        Params:
            list notifiers: the configured notifiers to push to
        """
        self.notifiers = notifiers
        self.threadpool = Threadpool(5)

    def receive_event(self, event):
        """
        Starts the thread to push notifications

        Params:
            Event event: The event to notify of
        """
        self.run(event)

    def run(self, event):
        """
        Sends a notification to each configured
        notifier passed in for the given host
        and event.

        Params:
            array  notifiers: the notifiers to sent a notification through
            string host:      the hostname the notification applies to
            dict   event:     the event (contains a message and title)
        """
        for n in self.notifiers:
            notify = n(event)
            self.threadpool.add(notify.run)

if __name__ == "__main__":
    pass
