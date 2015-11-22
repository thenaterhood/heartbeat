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
from heartbeat.modules import EventDispatcher
from heartbeat.modules import MonitorHandler
from heartbeat.api import SignalType
from heartbeat.monitoring import Monitor
from heartbeat.platform import Event

import concurrent.futures

class TestDispatcher(unittest.TestCase):

    def setUp(self):
        self.event = Event()
        self.ran_compare = False

    def test_init(self):
        d = EventDispatcher()

    def test_hook_attach(self):
        d = EventDispatcher()
        d.hook_attach(SignalType.NEW_EVENT, self._compare_event_from_sig)

        hooks = d.hooks
        self.assertTrue(self._compare_event_from_sig in hooks[SignalType.NEW_EVENT])

    def test_put_event(self):
       d = EventDispatcher()
       d.hook_attach(SignalType.NEW_EVENT, self._compare_event_from_sig)

       hooks = d.hooks
       self.assertTrue(self._compare_event_from_sig in hooks[SignalType.NEW_EVENT])

       d.put_event(self.event)
       self.assertTrue(self.ran_compare)

    def _compare_event_from_sig(self, s):
        self.ran_compare = True
        e = s.callback()
        self.assertEquals(self.event.__hash__(), e.__hash__())
