import unittest
import sys
if (sys.version_info < (3, 3)):
    from mock import MagicMock
    from mock import Mock
else:
    from unittest.mock import MagicMock
    from unittest.mock import Mock

from heartbeat.network import SocketBroadcaster
from heartbeat.modules import EventServer
from heartbeat.monitoring import MonitorHandler
from heartbeat.multiprocessing import Cache
from heartbeat.platform import Event, Topics
from heartbeat.plugin import Plugin
import logging
import datetime

import concurrent.futures

class TestDispatcher(unittest.TestCase):

    def setUp(self):
        self.tp = MagicMock(
                name="threadpool",
                spec=concurrent.futures.ThreadPoolExecutor,
                logger=Mock(name='logger', spec=logging.Logger)
                )
        self.event_cache = Mock(name='eventcache', spec=Cache)
        self.event_time_cache = Mock(name='eventcache', spec=Cache)
        self.event = Event()
        self.notifier = Mock(name="n1", spec=Plugin)
        self.event.type = Topics.DEBUG
        self.ran_compare = False
        self.eventserver = EventServer(
                self.tp,
                event_cache=self.event_cache,
                event_time_cache=self.event_time_cache
                )
        self.eventserver.eventTime = self.event_time_cache
        self.eventserver.monitorPreviousEvent = self.event_cache

    def test_init(self):
        d = EventServer(
                MagicMock(
                    name="threadpool",
                    spec=concurrent.futures.ThreadPoolExecutor
                    ),
                event_cache=self.event_cache,
                event_time_cache=self.event_time_cache
                )

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

        self.eventserver.eventTime.read = MagicMock(return_value=e.when)
        self.assertFalse(self.eventserver.event_delay_passed(e))

        delta = datetime.timedelta(hours=2)
        hours_ago = e.timestamp - delta
        self.eventserver.eventTime.read = MagicMock(
                return_value=hours_ago.timestamp()
                )
        self.assertTrue(self.eventserver.event_delay_passed(e))

    def test__check_call_status(self):
        f = concurrent.futures.Future()
        f.set_exception(None)
        self.eventserver.logger.error = MagicMock(return_value=None)

        self.eventserver._check_call_status(f)
        e = Exception("test exception")
        f.set_exception(e)
        self.eventserver._check_call_status(f)
        self.eventserver.logger.error.assert_called_once_with("Handler: " + str(e) + " at " + " -- ")

    def _compare_event_from_sig(self, e):
        self.ran_compare = True
        self.assertEquals(self.event.__hash__(), e.__hash__())
