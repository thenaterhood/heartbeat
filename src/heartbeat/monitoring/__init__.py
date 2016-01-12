from heartbeat.plugin import Plugin
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

    def __init__(self, event_callback, threadpool, logger=None, timer=None):
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
            framesummary = traceback.extract_tb(error.__traceback__)[-1]
            location = "{:s}:{:d}".format(framesummary.filename, framesummary.lineno)
            self.logger.error("Producer: " + str(error) + " at " + location)


class Monitor(Plugin):

    def __init__(self, callback):
        """
        Constructor

        Params:
            Function callback: A method to call when the MonitorWorker
                discovers something of note, or just feels lonely

        @deprecated: Plugins should now inherit directly from
        the Plugin class. This Monitor class will be removed
        in a future version and is provided only as scaffolding
        so legacy plugins continue to work.
        """
        self.callback = None
        self.realtime = False
        self.shutdown = False

    def get_producers(self):
        """
        Returns the available producers from the
        monitoring plugin. These are returned as
        a dictionary mapping MonitorType => call.

        For backwards compatibility, this will check
        for the legacy fields and generate a dictionary
        from that information if not overridden, using the
        proxy run method that allows legacy plugins to
        work with the new plugin architecture.
        """
        producers = {}

        if (self.realtime):
            producers[MonitorType.REALTIME] = self._proxy_run
        else:
            producers[MonitorType.PERIODIC] = self._proxy_run

        return producers

    def _proxy_run(self, callback):
        """
        @deprecated
        TODO:
        Proxy so that legacy plugins can be used with the new architecture
        without breaking. This sets the callback then calls the run method
        so things still behave as expected. This will be removed in a future
        version when breaking API changes are introduced
        """
        self.callback = callback
        self.run()

    def run(self):
        """
        @deprecated
        TODO:
        Runs the thing. Usually called from the parent start().
        This declaration will be removed in a future version, although
        children may still choose to implement it.
        """
        raise NotImplementedError("This method is not implemented.")
