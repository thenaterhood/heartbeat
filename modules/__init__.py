from time import sleep
import threading
from random import randint
import datetime
import operator
from network import NetworkInfo
from network import SocketListener
from network import SocketBroadcaster
from notifiers import Event
from notifiers import Notification

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

        super().__init__()

    def _beat(self):
        """
        Broadcasts a single beat
        """
        netinfo = NetworkInfo()
        data = self.secret+bytes(netinfo.fqdn.encode("UTF-8"))
        self.bcaster.push(data)
        print("beat")

    def run(self):
        """
        Runs the heartbeat (typically started by the thread start() call)
        """
        while 1:
          self._beat()
          sleep(5 * randint(1,5) )

class HeartMonitor(threading.Thread):
    """
    A monitor class to listen for and handle the known heartbeats on the
    network.
    """
    def __init__(self, port, secret, notifiers):
        """
        constructor

        Params:
            int port: the port to listen on. Must match that of the heartbeats this
               is intended to watch
            string secret: a secret string to identify the heartbeat. Must match
               that of the heartbeats this is intended to watch
            array notifiers: an array of notifier classes to call to send
                notifications of events
        """
        self.port = port
        self.known_hosts = []
        self.secret = bytes(secret.encode("UTF-8"))
        self.notifiers = notifiers
        self.notifier = Notification(notifiers)
        self.listener = SocketListener(port, self.receive)

        super().__init__()

    def _bcastIsOwn( self, host ):
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
        if data.startswith(self.secret) and not self._bcastIsOwn( data[len(self.secret):].decode("UTF-8") ):
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
        sorted_hosts = sorted(self.known_hosts.items(), key=operator.itemgetter(1))
        print( self.known_hosts )
        i = 0
        while ( i < len(sorted_hosts) and datetime.datetime.now() - sorted_hosts[i][1] > datetime.timedelta(seconds=60) ):
            print( "Removing flatlined host: ", sorted_hosts[i][0] )
            event = Event("Flatlined Host", "Host flatlined (heartbeat lost)", sorted_hosts[i][0])
            self.notifier.push(event)
            self.known_hosts.remove(sorted_hosts[i][0])
            i += 1

    def run(self):
        """
        Runs the monitor. Usually called by the parent start()
        """
        self.known_hosts = LockingDictionary()
        self.listener.start()

        while True:
            sleep(40)
            self._cleanup_hosts()

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

