import queue
import threading
import datetime
import json


class NotifyWorker(threading.Thread):

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
        super(NotifyWorker, self).__init__()

    def run(self):
        raise NotImplementedError


class Event:

    """
    An event to notify of. Contains a title, message, and timestamp
    """
    __slots__ = ('title', 'message', 'timestamp', 'host', 'one_time')

    def __init__(self, title='', message='', host="localhost"):
        """
        Constructor

        Params:
            string title:   the title of the event
            string message: the message describing the event
        """
        self.title = title
        self.message = message
        self.timestamp = datetime.datetime.now()
        self.host = host
        self.one_time = False

    def to_json(self):
        dictionary = dict()
        dictionary['title'] = self.title
        dictionary['message'] = self.message
        dictionary['host'] = self.host
        dictionary['one_time'] = self.one_time

        return json.dumps(dictionary)

    def load_json(self, jsonString):
        dictionary = json.loads(jsonString)

        self.title = dictionary['title']
        self.message = dictionary['message']
        self.host = dictionary['host']
        self.one_time = dictionary['one_time']


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
