import unittest

from heartbeat.platform import Event
from heartbeat.monitoring import Monitor

class TestMonitor(unittest.TestCase):

    def setUp(self):
        pass

    def test_instantiate(self):
        monitor = Monitor(None)
        
        self.assertEqual(False, monitor.realtime)
        self.assertEqual(False, monitor.shutdown)
        self.assertEqual(None, monitor.callback)
        
    def test_run(self):
        monitor = Monitor(None)
        
        self.assertRaises(NotImplementedError, monitor.run) 
