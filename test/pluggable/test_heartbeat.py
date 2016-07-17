import unittest
import sys
if (sys.version_info < (3, 3)):
    from mock import MagicMock
    from mock import Mock
    from mock import ANY
else:
    from unittest.mock import MagicMock
    from unittest.mock import Mock
    from unittest.mock import ANY

from heartbeat.pluggable.heartbeat import Pulse, PulseMonitor
from heartbeat.network import SocketBroadcaster, SocketListener, NetworkInfo
from heartbeat.platform import Event, Topics
from heartbeat.monitoring import MonitorHandler, MonitorType
from heartbeat.multiprocessing import Cache, BackgroundTimer
from pymlconf import ConfigManager

import datetime
from time import time

import concurrent.futures


class TestPulse(unittest.TestCase):

    def setUp(self):
        self.timer = Mock(name='timer', spec=BackgroundTimer)
        self.netinfo = Mock(name='network', spec=NetworkInfo)
        self.hb = Pulse(self.timer, self.netinfo)

    def test_instantiate(self):
        hb = Pulse(self.timer, self.netinfo)

    def test_beat(self):
        func = MagicMock(return_value=None)
        self.hb.callback = func
        self.hb._beat()

        func.assert_called_once_with(ANY)


class TestPulseMonitor(unittest.TestCase):

    def setUp(self):
        self.cache = Mock(name='cache', spec=Cache)
        self.monitor = PulseMonitor(
                cache=self.cache,
                )

    def test_init(self):
        monitor = PulseMonitor(
                cache=self.cache,
                )

        self.assertEqual(self.cache, monitor.cache)

    def test_get_producers(self):
        prods = self.monitor.get_producers()
        correct = {
                MonitorType.PERIODIC: self.monitor.cleanup_hosts,
                MonitorType.REALTIME: self.monitor.set_callback
                }

        self.assertEqual(correct, prods)

    def test_get_subscriptions(self):
        subs = self.monitor.get_subscriptions()
        correct = {
                Topics.HEARTBEAT: self.monitor.receive
                }

        self.assertEqual(correct, subs)

    def test__log_host(self):

        self.monitor.cache.write = MagicMock(return_value=None)
        self.monitor.cache.keys = MagicMock(return_value=[])
        self.monitor.callback = MagicMock()

        self.monitor._log_host('foo.example.com')
        self.monitor.cache.write.assert_called_with('foo.example.com', ANY)
        self.monitor.callback.assert_called_with(ANY)

        self.monitor._log_host('foo.example.com')
        self.monitor.cache.write.assert_called_with('foo.example.com', ANY)

    def test_cleanup_hosts(self):

        self.monitor.cache.write = MagicMock(return_value=None)
        self.monitor.cache.keys = MagicMock(return_value=['foo.example.com'])
        self.monitor.cache.items = MagicMock(return_value=[('foo.example.com', 1453848040.6469207)])
        self.monitor.callback = MagicMock()
        self.monitor.cache.read = MagicMock(return_value=datetime.datetime(year=1970, month=1, day=1))

        cb = MagicMock(return_value=None)
        self.monitor.cleanup_hosts(cb)
        cb.assert_called_once_with(ANY)

    def test_cleanup_hosts_no_expired(self):
        self.monitor.cache.write = MagicMock(return_value=None)
        self.monitor.cache.keys = MagicMock(return_value=['foo.example.com'])
        self.monitor.cache.items = MagicMock(return_value=[('foo.example.com', time())])
        self.monitor.callback = MagicMock()
        self.monitor.cache.read = MagicMock(return_value=datetime.datetime(year=1970, month=1, day=1))

        cb = MagicMock(return_value=None)
        self.monitor.cleanup_hosts(cb)
