import unittest
import sys
if (sys.version_info < (3, 3)):
    from mock import MagicMock
    from mock import Mock
else:
    from unittest.mock import MagicMock
    from unittest.mock import Mock

from heartbeat.modules import Heartbeat
from heartbeat.network import SocketBroadcaster
from heartbeat.modules import EventServer
from heartbeat.monitoring import MonitorHandler
from heartbeat.monitoring import Monitor
from heartbeat.notifications import Notifier
from heartbeat.platform import Event, Topics
import datetime

import concurrent.futures

class TestDispatcher(unittest.TestCase):

    def setUp(self):
        self.tp = MagicMock(name="threadpool", spec=concurrent.futures.ThreadPoolExecutor)
        self.event = Event()
        self.notifier = Mock(name="n1", spec=Notifier)
        self.event.type = Topics.DEBUG
        self.ran_compare = False
        self.eventserver = EventServer(self.tp)

    def test_init(self):
        d = EventServer(MagicMock(name="threadpool", spec=concurrent.futures.ThreadPoolExecutor))

    def test_attach(self):
        self.eventserver.attach(Topics.DEBUG, self._compare_event_from_sig)

        topics = self.eventserver.topics
        self.assertTrue(self._compare_event_from_sig in topics[Topics.DEBUG])

    def test_put_event(self):
       self.eventserver.attach(Topics.DEBUG, self._compare_event_from_sig)

       topics = self.eventserver.topics
       self.assertTrue(self._compare_event_from_sig in topics[Topics.DEBUG])

       self.eventserver.put_event(self.event)
       self.tp.submit.assert_called_once_with(self.eventserver.topics[Topics.DEBUG][0], self.event)

    def test_event_delay_passed(self):
        e = Event()

        self.eventserver.eventTime.write(e.__hash__(), e.timestamp)
        self.assertFalse(self.eventserver.event_delay_passed(e))

        delta = datetime.timedelta(hours=2)
        hours_ago = e.timestamp - delta
        self.eventserver.eventTime.write(e.__hash__(), hours_ago)
        self.assertTrue(self.eventserver.event_delay_passed(e))

    def _compare_event_from_sig(self, e):
        self.ran_compare = True
        self.assertEquals(self.event.__hash__(), e.__hash__())
