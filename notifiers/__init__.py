import queue
import threading
import datetime

class NotifyWorker(threading.Thread):
    """
    A notify worker thread for notifiers to extend.
    Defines a common interface and a thread so that
    notifications can eventually be queued.

    Extends:
        threading.Thread
    """

    def __init__(self, host, event):
        """
        constructor

        Params:
            string host:  the hostname of the system to notify for
            Event   event: the event details (message and title)
        """
        self.host = host
        self.event = event

    def run(self):
        raise NotImplementedError

class Event:
    """
    An event to notify of. Contains a title, message, and timestamp
    """
    __slots__ = ('title', 'message', 'timestamp')

    def __init__(self, title, message):
        """
        Constructor

        Params:
            string title:   the title of the event
            string message: the message describing the event
        """
        self.title = title
        self.message = message
        self.timestamp = datetime.datetime.now()

def send_notification(notifiers, host, event):
    """
    Sends a notification to each configured
    notifier passed in for the given host
    and event.

    Params:
        array  notifiers: the notifiers to sent a notification through
        string host:      the hostname the notification applies to
        dict   event:     the event (contains a message and title)
    """
    for n in notifiers:
        notify = n(host, event)
        notify.run()
