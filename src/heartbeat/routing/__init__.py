import datetime
from heartbeat.platform import Topics
from heartbeat.multiprocessing import Cache
import logging
import traceback
from enum import Enum


class RateLimitHandler(object):

    """
    Handles rate limiting events
    """

    def __init__(self, topic_strategies=None, event_cache=None, time_cache=None):
        """
        Constructor

        Params:
            dict() strategies: mapping of event types to limit strategies
            Cache event_cache
            Cache time_cache
        """

        if topic_strategies is None:
            topic_strategies = {
                Topics.WARNING: self.event_different_from_previous,
                Topics.INFO: self.event_different_from_previous,
                Topics.DEBUG: self.event_different_from_previous,
                Topics.VIRT: self.event_different_from_previous,
                Topics.HEARTBEAT: self.always_allow,
                Topics.STARTUP: self.always_allow
            }

        self.topic_strategies = topic_strategies

        if event_cache is None:
            event_cache = Cache('EventServerevent-previous-cache')

        self.event_cache = event_cache

        if time_cache is None:
            time_cache = Cache('EventServerevent-time-cache')

        self.time_cache = time_cache

    def always_allow(self, event):
        return True

    def event_different_from_previous(self, event):
        """
        Checks if an event is the same as the previous received
        from the same notifier"
        """
        duplicate = False

        if (self.event_cache.exists(event.source)):
            previous = self.event_cache.read(event.source)
            duplicate = (previous == event.__hash__())

        return not duplicate

    def event_delay_passed(self, event):
        """
        Checks if a specific event happened repeatedly within two hours
        """
        delay_passed = True

        if (self.time_cache.exists(event.__hash__())):
            lastSeen = datetime.datetime.fromtimestamp(
                self.time_cache.read(event.__hash__())
                )
            two_hours_ago = datetime.timedelta(hours=2)
            delay_passed = (datetime.datetime.now() - lastSeen) > two_hours_ago

        return delay_passed

    def allow_event(self, event):
        """
        Whether an event should be allowed to be pushed

        Params:
            Event event
        Returns:
            bool
        """
        allow = False
        if not event.type in self.topic_strategies:
            allow = self.event_different_from_previous(event)

        else:
            allow = self.topic_strategies[event.type](event)

        if allow:
            self.log_event(event)

        return allow

    def log_event(self, event):
        """
        Stores the event time and logs the event as the latest
        from the particular monitor (no duplicate events in a row)
        """
        self.time_cache.write(event.__hash__(), event.when)
        self.event_cache.write(event.source, event.__hash__())
        self.time_cache.writeToDisk()
        self.event_cache.writeToDisk()


class EventRouter(object):

    """
    Handles dispatching events to subscribers based on the topic
    of the event.
    """

    def __init__(self, threadpool, limiter=None, logger=None):
        """
        Constructor

        Params:
            list notifiers: the configured notifiers to push to
            Func limit_strategy: the function to call when checking if an event
                should be thrown or not. None defaults to monitor-based
                (doesn't throw the same event twice in a row from a monitor)
        """
        if (logger is None):
            self.logger = logging.getLogger(
                __name__ + "." + self.__class__.__name__
            )
        else:
            self.logger = logger

        self.topics = {}
        for t in Topics:
            self.topics[t] = []

        if (limiter is None):
            limiter = RateLimitHandler()

        self.limiter = limiter

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
        self.logger.debug("%s has subscribed to %s", str(callback), str(topic))
        self.topics[topic].append(callback)

    def put_event(self, event):
        """
        Starts the thread to push notifications

        Params:
            Event event: The event to notify of
        """
        self.logger.info("Event Generated: %s", event.__str__())
        if (self.limiter.allow_event(event)):
            self.logger.debug("Dispatching Event")
            self._forward_event(event)
        else:
            self.logger.debug(
                "Skipping dispatch per limit strategy")

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
            self.logger.error("Handler: %s at %s", str(error), location)


if __name__ == "__main__":
    pass
