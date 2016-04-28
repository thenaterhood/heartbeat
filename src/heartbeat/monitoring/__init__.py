from enum import Enum
from heartbeat.multiprocessing import BackgroundTimer
import logging
import traceback


class MonitorType(Enum):
    """
    Monitor types; realtime or periodic
    """

    REALTIME = 'realtime'
    PERIODIC = 'periodic'


class MonitorHandler(object):

    """
    Monitoring class handling running multiple monitors on
    an interval
    """

    def __init__(self, event_callback, threadpool, interval=60, logger=None, timer=None):
        """
        Constructor

        Params:
            Callable event_callback: method to call when a new Event is received
            Threadpool threadpool: threadpool for running tasks.
            Logger logger: logger
            BackgroundTimer timer: Timer instance for running periodic queries
        """
        self.realtime_plugins = []
        self.periodic_plugins = []
        self.started = False

        if logger is None:
            self.logger = logging.getLogger(
                __name__ + "." + self.__class__.__name__
            )
        else:
            self.logger = logger

        self.event_callback = event_callback
        self.logger.debug("Bringing up threadpool")
        self.threadpool = threadpool
        if (timer is None):
            self.timer = BackgroundTimer(interval, True, self.scan)
        else:
            self.timer = timer

    def add_realtime_monitor(self, call):
        """
        Adds a realtime monitoring plugin

        Params:
            Callable call: the start or run method of the plugin
        """
        if self.started:
            raise Exception(
                "Plugins cannot be added to a running handler"
                )
        self.realtime_plugins.append(call)

    def add_periodic_monitor(self, call):
        """
        Adds a periodic monitoring plugin

        Params:
            Callable call: the run method of the plugin
        """
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
            f = self.threadpool.submit(m, self.event_callback)
            f.add_done_callback(self._check_call_status)

    def terminate(self):
        """
        Shuts down the thread cleanly
        """
        self.timer.stop()
        self.threadpool.terminate()

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
            self.logger.error("Producer: " + str(error) + " at " + location)
