import unittest
import sys
if (sys.version_info < (3, 3)):
    from mock import MagicMock
    from mock import Mock
else:
    from unittest.mock import MagicMock
    from unittest.mock import Mock
from heartbeat.notifications import Notifier
from heartbeat.platform import Event

class TestNotifier(unittest.TestCase):
	
	def setUp(self):
		self.notifier = Notifier()
		
	def test_instantiate(self):
		n = Notifier()
		
		self.assertEqual(None, n.event)
		
	def test_run(self):
		
		self.assertRaises(NotImplementedError, self.notifier.run)
		
	def test_load(self):
		
		e = Mock(name="event", spec=Event)
		
		self.notifier.load(e)
		
		self.assertEqual(e, self.notifier.event)
		