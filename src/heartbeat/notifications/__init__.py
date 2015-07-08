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

    def __init__(self):
        """
        constructor

        Params:
            string host:  the hostname of the system to notify for
            Event   event: the event details (message and title)
        """
        self.event = None

    def load(self, event):
        self.event = event
        host = event.host
        self.title = event.title + ": " + host
        date = datetime.datetime.now()
        self.message = host + ": " + event.message + " at " + \
            event.timestamp.strftime("%H:%M:%S %m/%d/%y")

    def run(self):
        raise NotImplementedError
