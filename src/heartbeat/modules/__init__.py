from time import sleep
import threading
from random import randint
import datetime
from queue import Queue
from heartbeat.network import NetworkInfo
from heartbeat.platform import Topics, get_config_manager
from heartbeat.multiprocessing import LockingDictionary, BackgroundTimer, Cache
from heartbeat.security import Encryptor
import logging
import traceback
import os
import json


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

        self.monitorPreviousEvent = Cache(
            self.__class__.__name__ + "event-previous-cache"
            )
        self.eventTime = Cache(self.__class__.__name__ + "event-time-cache")
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
        self.logger.info("Event Generated: " + str(event))
        if (self.limit_strategy(event)):
            self.logger.debug("Dispatching Event")
            self._forward_event(event)
        else:
            self.logger.debug(
                "Skipping dispatch per limit strategy")

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
            lastSeen = datetime.datetime.fromtimestamp(
                self.eventTime.read(event.__hash__())
                )
            two_hours_ago = datetime.timedelta(hours=2)
            delay_passed = (datetime.datetime.now() - lastSeen) > two_hours_ago

        return delay_passed

    def log_event(self, event):
        """
        Stores the event time and logs the event as the latest
        from the particular monitor (no duplicate events in a row)
        """
        self.eventTime.write(event.__hash__(), event.when)
        self.monitorPreviousEvent.write(event.source, event)
        self.eventTime.writeToDisk()
        self.monitorPreviousEvent.writeToDisk()

    def _forward_event(self, event):
        """
        Forwards an event to all the handlers subscribed to
        the topic the event is categorized as
        """
        for t in self.topics[event.type]:
            f = self.threadpool.submit(t, event)
            f.add_done_callback(self._check_call_status)

    def _check_call_status(self, f):
        """
        Checks the status of a completed (or crashed)
        submission to the handler threadpool. This
        method is intended to be submitted to the Future
        via add_done_callback, rather than being
        called directly.

        Params:
            Future f
        """
        error = f.exception(5)
        if error is None:
            return
        else:
            try:
                framesummary = traceback.extract_tb(error.__traceback__)[-1]
                location = "{:s}:{:d}".format(framesummary.filename, framesummary.lineno)
            except (AttributeError, IndexError):
                location = " -- "
            self.logger.error("Handler: " + str(error) + " at " + location)


if __name__ == "__main__":
    pass
