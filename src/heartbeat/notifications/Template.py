from heartbeat.notifications import Notifier
from datetime import datetime


class NotifyTemplate(Notifier):
    """
    @deprecated: this class was provided as a template
    for creating new Notifier plugins, but is now
    deprecated and will be removed in a future version.

    Classes should follow the new Plugin architecture
    """
    __slots__ = ('message', 'title')

    def __init__(self):
        super(NotifyTemplate, self).__init__()

    def run(self):
        # Push a notification to wherever
        pass
