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
from heartbeat.modules import MonitorHandler
from heartbeat.monitoring import Monitor
from heartbeat.platform import Event, Topics

import concurrent.futures

class TestDispatcher(unittest.TestCase):

    def setUp(self):
        self.event = Event()
        self.event.type = Topics.DEBUG
        self.ran_compare = False

    def test_init(self):
        d = EventServer()

    def test_attach(self):
        d = EventServer()
        d.attach(Topics.DEBUG, self._compare_event_from_sig)

        topics = d.topics
        self.assertTrue(self._compare_event_from_sig in topics[Topics.DEBUG])

    def test_put_event(self):
       d = EventServer()
       d.attach(Topics.DEBUG, self._compare_event_from_sig)

       topics = d.topics
       self.assertTrue(self._compare_event_from_sig in topics[Topics.DEBUG])

       d.put_event(self.event)
       self.assertTrue(self.ran_compare)

    def _compare_event_from_sig(self, e):
        self.ran_compare = True
        self.assertEquals(self.event.__hash__(), e.__hash__())
