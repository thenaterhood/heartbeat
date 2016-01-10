import unittest
import sys
from heartbeat.plugin import Plugin

class TestPlugin(unittest.TestCase):

    def setUp(self):
        self.plugin = Plugin()

    def test_get_subscriptions(self):
        """
        Test the stub method correctly returns an empty dict
        """
        self.assertEqual(self.plugin.get_subscriptions(), {})

    def test_get_producers(self):
        """
        Test the stub method correctly returns an empty dict
        """
        self.assertEqual(self.plugin.get_producers(), {})
