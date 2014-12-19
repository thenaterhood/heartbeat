import queue
import threading
import datetime
import json
import inspect


class Notifier():

    """
    A notify worker thread for notifiers to extend.
    Defines a common interface and a thread so that
    notifications can eventually be queued.

    Extends:
        threading.Thread
    """

    def __init__(self, event):
        """
        constructor

        Params:
            string host:  the hostname of the system to notify for
            Event   event: the event details (message and title)
        """
        self.event = event

    def run(self):
        raise NotImplementedError

class Notification(threading.Thread):

    """
    A class that holds a list of notifiers and allows them to
    all be kicked off in succession
    """

    def __init__(self, notifiers):
        """
        Constructor

        Params:
            list notifiers: the configured notifiers to push to
        """
        self.notifiers = notifiers
        super().__init__()

    def push(self, event):
        """
        Starts the thread to push notifications

        Params:
            Event event: The event to notify of
        """
        self.event = event
        self.run()

    def run(self):
        """
        Sends a notification to each configured
        notifier passed in for the given host
        and event.

        Params:
            array  notifiers: the notifiers to sent a notification through
            string host:      the hostname the notification applies to
            dict   event:     the event (contains a message and title)
        """
        for n in self.notifiers:
            notify = n(self.event)
            notify.run()
