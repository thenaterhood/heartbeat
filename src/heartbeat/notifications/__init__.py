import datetime
from heartbeat.plugin import Plugin
from heartbeat.platform import Topics


class Notifier(Plugin):

    """
    A notify worker thread for notifiers to extend.
    Defines a common interface and a thread so that
    notifications can eventually be queued.

    Extends:
        threading.Thread

    @deprecated: Classes should now inherit directly
    from the Plugin class. This Notifier class will
    be removed in a future version, but is still
    provided as scaffolding for legacy versions.
    """

    def __init__(self):
        """
        constructor

        Params:
            string host:  the hostname of the system to notify for
            Event   event: the event details (message and title)
        """
        self.event = None

    def _load_and_run(self, event):
        """
        @deprecated
        This method combines the "load" and "run"
        methods for backwards compatibility until the
        load and run workflow is fully converted to
        a single method in the next version of the API

        TODO: remove method when API is updated
        """
        self.load(event)
        self.run()

    def load(self, event):
        """
        @deprecated
        TODO: remove method in a future release
        """
        self.event = event
        host = event.host
        self.title = event.title + ": " + host
        date = datetime.datetime.now()
        self.message = host + ": " + event.message + " at " + \
            event.timestamp.strftime("%H:%M:%S %m/%d/%y")

    def get_subscriptions(self):
        """
        Return a dictionary of topics mapped to callbacks.
        This defaults to using the _load_and_run method
        to subscribe to the INFO, WARNING, and DEBUG topics
        which mimics the behaviour of legacy (<=2.6.0) versions
        """
        subs = {
            Topics.INFO: self._load_and_run,
            Topics.WARNING: self._load_and_run,
            Topics.DEBUG: self._load_and_run
        }

        return subs

    def run(self):
        """
        @deprecated

        This method is deprecated and will no longer be defined by
        the parent class. It can still be defined by the inheriting
        classes if desired. Heartbeat will request the method to
        call for each subscription instead
        """

        raise NotImplementedError
