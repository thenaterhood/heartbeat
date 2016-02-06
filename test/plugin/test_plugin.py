import unittest
import sys
if sys.version_info < (3, 3):
    from mock import Mock, MagicMock
else:
    from unittest.mock import Mock, MagicMock

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

    def test_get_services(self):
        self.assertEqual(self.plugin.get_services(), [])

    def test_get_dependencies(self):
        self.assertEqual(self.plugin.get_required_services(), [])

    def test_check_empty_dependencies(self):
        self.assertTrue(self.plugin.requirements_satisfied([]))
        self.assertTrue(self.plugin.requirements_satisfied(None))
        self.assertTrue(self.plugin.requirements_satisfied(['foo', 'bar']))

    def test_check_dependencies_satisfied(self):
        self.plugin.get_required_services = MagicMock(return_value=['foo', 'bar'])
        self.assertTrue(self.plugin.requirements_satisfied(['foo', 'bar']))
        self.assertTrue(self.plugin.requirements_satisfied(['foo', 'foo', 'bar']))
        self.assertTrue(self.plugin.requirements_satisfied(['bar', 'foo']))
        self.assertTrue(self.plugin.requirements_satisfied(['foo', 'bar', 'baz']))

    def test_check_dependencies_not_satisfied(self):
        self.plugin.get_required_services = MagicMock(return_value=['foo', 'bar'])
        self.assertFalse(self.plugin.requirements_satisfied([]))
        self.assertFalse(self.plugin.requirements_satisfied(['foo']))
        self.assertFalse(self.plugin.requirements_satisfied(['bar']))
        self.assertFalse(self.plugin.requirements_satisfied(['foo', 'baz']))
        self.assertFalse(self.plugin.requirements_satisfied(None))

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

