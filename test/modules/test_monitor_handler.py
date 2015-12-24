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
from heartbeat.platform import Event

import concurrent.futures


class TestMonitorHandler(unittest.TestCase):

    def setUp(self):
        self.hwmonitors = []
        self.hwmonitors.append(Mock(name="m1", spec=Monitor))
        self.hwmonitors.append(Mock(name="m2", spec=Monitor))

        self.hwmonitors[0].realtime=False

        notifyHandler = MagicMock(name="dispatcher", spec=EventServer)

        pool = MagicMock(name="threadpool", spec=concurrent.futures.ThreadPoolExecutor)

        self.monitor_handler = MonitorHandler(
                self.hwmonitors,
                notifyHandler.put_event,
                pool
                )

        self.monitor_handler.hwmonitors = self.hwmonitors

    def test_scan(self):
        self.monitor_handler.scan()
        self.monitor_handler.threadpool.submit.assert_called_with(self.hwmonitors[1].run)

    def test_receive_event(self):
        e = Event()
        self.monitor_handler.receive_event(e)

        self.monitor_handler.event_callback.assert_called_once_with(e)


