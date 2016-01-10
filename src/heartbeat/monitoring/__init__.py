from heartbeat.plugin import Plugin
from enum import Enum


class MonitorType(Enum):
    """
    Monitor types; realtime or periodic
    """

    REALTIME = 'realtime'
    PERIODIC = 'periodic'


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
