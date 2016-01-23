from time import sleep
import threading
from random import randint
import datetime
from queue import Queue
from heartbeat.network import NetworkInfo
from heartbeat.platform import Topics, get_config_manager
from heartbeat.multiprocessing import LockingDictionary, BackgroundTimer
from heartbeat.security import Encryptor
import logging
import traceback
import os
import json
from hashlib import sha256


class Cache(LockingDictionary):

    """
    Handles a persistant cache for storing key-value
    pairs.
    """

    def __init__(self, cache_name, reset=False, settings=None, encryptor=None):
        """
        Parameters:
            str name: The name of the cache
            bool reset: If the cache should be reset if its artifacts already exist
        """
        if settings is None:
            settings = get_config_manager()

        self.directory = settings.heartbeat.cache_dir

        if encryptor is None:
            self.encryptor = Encryptor(settings.heartbeat.secret_key)
        else:
            self.encryptor = encryptor

        super(Cache, self).__init__()
        self.cache_name = cache_name
        if not reset:
            self._load_from_disk()

    def resetValuesTo(self, value):
        """
        Resets all the cache values to a specified value
        """
        self._semaphore.acquire()
        for k in self._dictionary.keys():
            self._dictionary[k] = value
        self._semaphore.release()

    def writeToDisk(self):
        """
        Writes the cache out to disk
        """
        print("Writing cache to disk")
        try:
            with open(self._get_filename(), "wb") as cacheFile:
                data = self.encryptor.encrypt(json.dumps(self._dictionary))
                cacheFile.write(data)
        except Exception as e:
            print(e)

    def _load_from_disk(self):
        """
        Loads the cache from disk
        """
        self._semaphore.acquire()
        try:
            with open(self._get_filename(), "r") as cachefile:
                fcontents = cachefile.read()
                decrypted = self.encryptor.decrypt(fcontents)
                self._dictionary = json.loads(decrypted)
        except Exception as e:
            print(e)
            self._dictionary = {}
        self._semaphore.release()

    def _get_filename(self):
        """
        Generates the filename for the cache
        """
        return os.path.join(
            self.directory,
            sha256(self.cache_name.encode("UTF-8")).hexdigest()
            )


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
            framesummary = traceback.extract_tb(error.__traceback__)[-1]
            location = "{:s}:{:d}".format(framesummary.filename, framesummary.lineno)
            self.logger.error("Handler: " + str(error) + " at " + location)


if __name__ == "__main__":
    pass
