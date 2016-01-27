import unittest
import sys
if sys.version_info < (3, 3):
    from mock import Mock
else:
    from unittest.mock import Mock

from heartbeat.plugin import Plugin, PluginRegistry
from pymlconf import ConfigManager

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

class TestPluginRegistry(unittest.TestCase):

    def setUp(self):
        self.pr = PluginRegistry
        self.settings = Mock(name="settings", spec=ConfigManager)
        self.settings.heartbeat = Mock(name="hbnamespace", spec=ConfigManager)
        self.settings.heartbeat.plugins = ['foo.foo', 'bar.bar', 'baz.baz']

    def test_populate_from_settings(self):

        print(self.settings.heartbeat.plugins)
        self.pr.populate_from_settings(self.settings)

        self.assertTrue('foo.foo' in self.pr.whitelist)
        self.assertTrue('bar.bar' in self.pr.whitelist)
        self.assertTrue('baz.baz' in self.pr.whitelist)

