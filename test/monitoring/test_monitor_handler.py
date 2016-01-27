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
from heartbeat.platform import Event
from heartbeat.plugin import Plugin

import logging
import concurrent.futures


class TestMonitorHandler(unittest.TestCase):

    def setUp(self):
        self.hwmonitors = []
        self.hwmonitors.append(Mock(name="m1", spec=Plugin))
        self.hwmonitors.append(Mock(name="m2", spec=Plugin))

        self.hwmonitors[0].realtime=False

        self.notifyHandler = MagicMock(name="dispatcher", spec=EventServer)

        pool = MagicMock(name="threadpool", spec=concurrent.futures.ThreadPoolExecutor)

        self.monitor_handler = MonitorHandler(
                self.notifyHandler.put_event,
                pool,
                MagicMock(name="logger", spec=logging.Logger)
                )

        self.monitor_handler.hwmonitors = self.hwmonitors

    def test_scan(self):
        # This is a lazy workaround to building a custom mock class, when
        # we only need to check one simple method call
        self.monitor_handler.add_periodic_monitor(self.hwmonitors[1].get_producers)
        self.monitor_handler.scan()
        self.monitor_handler.threadpool.submit.assert_called_with(
            self.hwmonitors[1].get_producers, self.notifyHandler.put_event
        )

    def test__check_call_status(self):
        f = concurrent.futures.Future()
        f.set_exception(None)
        self.monitor_handler.logger.error = MagicMock(return_value=None)

        self.monitor_handler._check_call_status(f)
        e = Exception("test exception")
        f.set_exception(e)
        self.monitor_handler._check_call_status(f)
        self.monitor_handler.logger.error.assert_called_once_with("Producer: " + str(e) + " at " + " -- ")
