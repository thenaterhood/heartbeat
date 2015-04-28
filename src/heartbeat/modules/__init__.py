from time import sleep
import os
import threading
from random import randint
import datetime
import operator
from queue import Queue
from heartbeat.network import NetworkInfo
from heartbeat.network import SocketListener
from heartbeat.network import SocketBroadcaster
from heartbeat.platform import Event
from heartbeat.multiprocessing import Threadpool
from heartbeat.multiprocessing import LockingDictionary
import logging


class Heartbeat(threading.Thread):

    """
    Defines a heartbeat thread which will send a broadcast
    over the network every given interval (plus a small random margin
    so as to avoid flooding the network)

    Extends threading.Thread
    """

    def __init__(self, interval, secret, bcaster):
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
        self._logger = logging.getLogger(
                __name__ + "." + self.__class__.__name__
                )

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

    def __init__(self, hwmonitors, notifyHandler, logger=None):
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
        realtimeMonitors = 0
        for m in hwmonitors:
            monitor = m(self.receive_event)
            if monitor.realtime:
                realtimeMonitors += 1
                self.rtMonitors.append(monitor)
            else:
                self.hwmonitors.append(monitor)

        self.notifier = notifyHandler
        self.shutdown = False
        self.logger.debug("Bringing up threadpool")
        self.threadpool = Threadpool(5 + realtimeMonitors, "MonitorPool")
        super(MonitorHandler, self).__init__()

    def run(self):
        """
        Run method, generally called from the parent start()
        """
        self.logger.debug("Starting realtime monitors")
        for m in self.rtMonitors:
            self.threadpool.add(m.run)

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
            self.threadpool.add(m.run)

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
        self.notifier.receive_event(event)

class _NotificationHandlerWorker(threading.Thread):

    """
    A worker for the notification handler so notifications
    can be processed asynchronously
    """

    def __init__(self, queue, notifiers, parent):
        super(_NotificationHandlerWorker, self).__init__()
        self.queue = queue
        self.notifiers = notifiers
        self.parent = parent
        self.threadpool = Threadpool(5, "NotificationWorkerThreadpool")
        self.daemon = True
        self._logger = logging.getLogger(
                __name__ + "." + self.__class__.__name__
                )
        self._logger.debug("Worker primed")

    def run(self):
        self._logger.debug("Starting work")
        self.parent.processing = True
        while not self.queue.empty():
            event = self.queue.get()
            self._logger.debug("Working on dispatching event " + str(event.__hash__()))
            for n in self.notifiers:
                self._logger.debug("Dispatching event " + str(event.__hash__()) + " to " + n.__class__.__name__)
                n.load(event)
                self.threadpool.add(n.run)

            self.queue.task_done()

        self._logger.debug("Worker terminating")
        self.parent.processing = False

class NotificationHandler():

    """
    A class that holds a list of notifiers and allows them to
    all be kicked off in succession
    """

    def __init__(self, notifiers, limit_strategy=None, logger=None):
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
            self.logger.debug("Skipping notification dispatch per limit strategy")

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
        self.log_event(event)
        self.queue.put(event)

        if not self.processing:
            processor = _NotificationHandlerWorker(self.queue, self.notifiers, self)
            processor.start()


if __name__ == "__main__":
    pass
