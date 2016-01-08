from time import sleep
import threading
from random import randint
import datetime
from queue import Queue
from heartbeat.network import NetworkInfo
from heartbeat.platform import Topics
from heartbeat.multiprocessing import LockingDictionary, BackgroundTimer
import logging


class Heartbeat(object):

    """
    Defines a heartbeat thread which will send a broadcast
    over the network every given interval (plus a small random margin
    so as to avoid flooding the network)
    """

    def __init__(self, interval, secret, bcaster, logger=None, timer=None):
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

        self.timer = timer
        if (timer is None):
            self.timer = BackgroundTimer(5*randint(1,5), True, self._beat)

        if (logger == None):
            self._logger = logging.getLogger(
                __name__ + "." + self.__class__.__name__
            )
        else:
            self._logger = logger

    def terminate(self):
        """
        Shuts down the thread cleanly
        """
        self._logger.info("Shutting down heartbeat broadcast")
        self.timer.stop()

    def _beat(self):
        """
        Broadcasts a single beat
        """
        netinfo = NetworkInfo()
        data = self.secret + bytes(netinfo.fqdn.encode("UTF-8"))
        self._logger.info("Broadcasting heartbeat")
        self.bcaster.push(data)

    def start(self):
        """
        Runs the heartbeat (typically started by the thread start() call)
        """
        self.timer.start()


class MonitorHandler(object):

    """
    Monitoring class handling running multiple monitors on
    an interval
    """

    def __init__(self, event_callback, threadpool, logger=None, timer=None):
        """
        Constructor

        Params:
            array[Monitor] hwmonitors: an array of HardwareWorker
                instances
            NotificationHandler notifyHandler:  notification handler
        """
        self.realtime_plugins = []
        self.periodic_plugins = []
        self.started = False

        if (logger == None):
            self.logger = logging.getLogger(
                __name__ + "." + self.__class__.__name__
            )
        else:
            self.logger = logger

        self.event_callback = event_callback
        self.logger.debug("Bringing up threadpool")
        self.threadpool = threadpool
        if (timer is None):
            self.timer = BackgroundTimer(60, True, self.scan)
        else:
            self.timer = timer

    def add_realtime_monitor(self, call):
        if self.started:
            raise Exception(
                "Plugins cannot be added to a running handler"
                )
        self.realtime_plugins.append(call)

    def add_periodic_monitor(self, call):
        if self.started:
            raise Exception(
                "Plugins cannot be added to a running handler"
                )
        self.periodic_plugins.append(call)

    def start(self):
        """
        Run method, generally called from the parent start()
        """
        self.started = True
        self.logger.debug("Starting realtime monitors")
        for m in self.realtime_plugins:
            self.threadpool.submit(m, self.event_callback)

        self.scan()
        self.timer.start()

    def scan(self):
        """
        Runs each monitor thread and waits for it to complete
        """
        self.logger.debug("Starting periodic query to monitors")
        for m in self.periodic_plugins:
            self.logger.debug("Querying " + str(m))
            self.threadpool.submit(m, self.event_callback)

    def terminate(self):
        """
        Shuts down the thread cleanly
        """
        self.timer.stop()
        self.threadpool.terminate()


class EventServer(object):

    """
    Handles dispatching events to subscribers based on the topic
    of the event.
    """

    def __init__(self, threadpool, limit_strategy=None, logger=None):
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

        self.topics = {}
        for t in Topics:
            self.topics[t] = []

        self.monitorPreviousEvent = LockingDictionary()
        self.eventTime = LockingDictionary()
        if (limit_strategy == None):
            self.limit_strategy = self.event_different_from_previous
        else:
            self.limit_strategy = limit_strategy

        self.threadpool = threadpool

    def attach(self, topic, callback):
        """
        Allows other systems to subscribe to events
        of different topics.

        Params:
            Topic topic: topic to subscribe to
            Callable callback: Method to call when a new event of the topic
                is received
        """
        self.logger.debug(str(callback) + " has subscribed to " + str(topic))
        self.topics[topic].append(callback)

    def put_event(self, event):
        """
        Starts the thread to push notifications

        Params:
            Event event: The event to notify of
        """
        self.logger.info("Received event: " + str(event))
        if (self.limit_strategy(event)):
            self.logger.debug("Dispatching event")
            self._forward_event(event)
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

    def _forward_event(self, event):
        """
        Forwards an event to all the handlers subscribed to
        the topic the event is categorized as
        """
        for t in self.topics[event.type]:
            self.threadpool.submit(t, event)


if __name__ == "__main__":
    pass
