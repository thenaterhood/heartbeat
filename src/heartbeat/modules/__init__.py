from time import sleep
import threading
from random import randint
import datetime
from queue import Queue
from heartbeat.network import NetworkInfo
from heartbeat.multiprocessing import LockingDictionary
from heartbeat.api import Signal, SignalType
import logging


class EventDispatcher(object):
    __slots__ = ('hooks')

    def __init__(self):
        self.hooks = {}
        for s in SignalType:
            self.hooks[s] = []

    def put_event(self, event, signal_type=SignalType.NEW_HUM_EVENT):

        self._send_event_signal(event, signal_type)
        if (signal_type != SignalType.NEW_EVENT):
            self._send_event_signal(event, SignalType.NEW_EVENT)

    def hook_attach(self, signal_type, call):
        self.hooks[signal_type].append(call)

    def _send_event_signal(self, event, signal_type):
        signal = Signal(signal_type, lambda: event)
        for r in self.hooks[signal_type]:
            r(signal)

    def _send_poll_signal(self):
        signal = Signal(SignalType.POLL, self.put_event)
        for r in self.hooks[SignalType.POLL]:
            r(signal)


class Heartbeat(threading.Thread):

    """
    Defines a heartbeat thread which will send a broadcast
    over the network every given interval (plus a small random margin
    so as to avoid flooding the network)

    Extends threading.Thread
    """

    def __init__(self, interval, secret, bcaster, logger=None):
        """
        constructor

        Params:
            int    port:     the port number to broadcast on
            int    interval: the base interval to use for beats
            string secret:   a secret string to identify the heartbeat
        """
        self.interval = interval
        self.secret = bytes(secret.encode("UTF-8"))
        self.bcaster = bcaster

        self.shutdown = False

        if (logger == None):
            self._logger = logging.getLogger(
                __name__ + "." + self.__class__.__name__
            )
        else:
            self._logger = logger

        super().__init__()

    def terminate(self):
        """
        Shuts down the thread cleanly
        """
        self._logger.info("Shutting down heartbeat broadcast")

    def _beat(self):
        """
        Broadcasts a single beat
        """
        netinfo = NetworkInfo()
        data = self.secret + bytes(netinfo.fqdn.encode("UTF-8"))
        self._logger.info("Broadcasting heartbeat")
        self.bcaster.push(data)

    def run(self):
        """
        Runs the heartbeat (typically started by the thread start() call)
        """
        while not self.shutdown:
            self._beat()
            sleep(5 * randint(1, 5))

        self.terminate()


class MonitorHandler(threading.Thread):

    """
    Monitoring class handling running multiple monitors on
    an interval
    """

    def __init__(self, hwmonitors, notifyHandler, threadpool, logger=None):
        """
        Constructor

        Params:
            array[Monitor] hwmonitors: an array of HardwareWorker
                instances
            NotificationHandler notifyHandler:  notification handler
        """
        self.hwmonitors = []
        self.rtMonitors = []
        if (logger == None):
            self.logger = logging.getLogger(
                __name__ + "." + self.__class__.__name__
            )
        else:
            self.logger = logger
        for m in hwmonitors:
            monitor = m(self.receive_event)
            if monitor.realtime:
                self.rtMonitors.append(monitor)
            else:
                self.hwmonitors.append(monitor)

        self.notifier = notifyHandler
        self.shutdown = False
        self.logger.debug("Bringing up threadpool")
        self.threadpool = threadpool
        super(MonitorHandler, self).__init__()

    def run(self):
        """
        Run method, generally called from the parent start()
        """
        self.logger.debug("Starting realtime monitors")
        for m in self.rtMonitors:
            self.threadpool.submit(m.run)

        while not self.shutdown:
            self.logger.debug("Starting periodic query to monitors")
            self.scan()
            sleep(60)

        self.terminate()

    def scan(self):
        """
        Runs each monitor thread and waits for it to complete
        """
        for m in self.hwmonitors:
            self.logger.debug("Querying " + m.__class__.__name__)
            self.threadpool.submit(m.run)

    def terminate(self):
        """
        Shuts down the thread cleanly
        """
        self.threadpool.terminate()

    def receive_event(self, event):
        """
        A callback method for monitors to call to. Currently just a
        wrapper for the notifier.push
        """
        self.notifier(event)


class NotificationHandler(object):

    """
    A class that holds a list of notifiers and allows them to
    all be kicked off in succession
    """

    def __init__(self, notifiers, threadpool, limit_strategy=None, logger=None):
        """
        Constructor

        Params:
            list notifiers: the configured notifiers to push to
            Func limit_strategy: the function to call when checking if an event
                should be thrown or not. None defaults to monitor-based
                (doesn't throw the same event twice in a row from a monitor)
        """
        if (logger == None):
            self.logger = logging.getLogger(
                __name__ + "." + self.__class__.__name__
            )
        else:
            self.logger = logger

        self.notifiers = []
        for n in notifiers:
            notifier = n()
            self.notifiers.append(notifier)

        self.queue = Queue(50)
        self.processing = False

        self.monitorPreviousEvent = LockingDictionary()
        self.eventTime = LockingDictionary()
        if (limit_strategy == None):
            self.limit_strategy = self.event_different_from_previous
        else:
            self.limit_strategy = limit_strategy

        self.threadpool = threadpool

    def receive_signal(self, signal):
        if (signal.signal_type == SignalType.NEW_HUM_EVENT):
            event = signal.callback()
            self.receive_event(event)

    def receive_event(self, event):
        """
        Starts the thread to push notifications

        Params:
            Event event: The event to notify of
        """
        self.logger.info("Received event: " + str(event))
        if (self.limit_strategy(event)):
            self.logger.debug("Dispatching notification")
            self.run(event)
        else:
            self.logger.debug(
                "Skipping notification dispatch per limit strategy")

    def event_different_from_previous(self, event):
        """
        Checks if an event is the same as the previous received
        from the same notifier"
        """
        duplicate = False

        if (self.monitorPreviousEvent.exists(event.source)):
            previous = self.monitorPreviousEvent.read(event.source)
            duplicate = (previous.__hash__() == event.__hash__())

        return not duplicate

    def event_delay_passed(self, event):
        """
        Checks if a specific event happened repeatedly within two hours
        """
        delay_passed = True

        if (self.eventTime.exists(event.__hash__())):
            lastSeen = self.eventTime.read(event.__hash__())
            two_hours_ago = datetime.timedelta(hours=2)
            delay_passed = (datetime.datetime.now() - lastSeen) > two_hours_ago

        return delay_passed

    def log_event(self, event):
        """
        Stores the event time and logs the event as the latest
        from the particular monitor (no duplicate events in a row)
        """
        self.eventTime.write(event.__hash__(), event.timestamp)
        self.monitorPreviousEvent.write(event.source, event)

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
            n.load(event)
            self.threadpool.submit(n.run)

        self.log_event(event)


if __name__ == "__main__":
    pass
