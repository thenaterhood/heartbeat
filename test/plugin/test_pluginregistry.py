import unittest
import sys
from heartbeat.plugin import Plugin, PluginRegistry


class TestPluginRegistry(unittest.TestCase):

    def setUp(self):
        PluginRegistry.whitelist = []
        PluginRegistry.plugins = []

    def test_auto_register(self):
        """
        Class inheriting from Plugin is correctly registered
        """

        PluginRegistry.whitelist.append("plugin.test_pluginregistry.MockPlugin")
        class MockPlugin(Plugin):
            """
            Fake plugin class to make sure importing operates
            correctly
            """
            pass

        self.assertTrue(MockPlugin in PluginRegistry.plugins)

    def test_auto_register_not_whitelisted(self):
        """
        Class inheriting from Plugin is ignored if not in whitelist
        """

        class MockPlugin(Plugin):
            """
            Fake plugin class
            """
            pass

        self.assertFalse(MockPlugin in PluginRegistry.plugins)

    def test_populate_whitelist(self):
        """
        Whitelist is properly populated only once
        """

        whitelist = ["plugin.test_pluginregistry.MockPlugin"]
        PluginRegistry.populate_whitelist(whitelist)

        self.assertEqual(whitelist, PluginRegistry.whitelist)

        self.assertRaises(Exception, lambda: PluginRegistry.populate_whitelist(whitelist))

        class MockPlugin(Plugin):
            """
            Fake plugin class
            """
            pass

        self.assertTrue(MockPlugin in PluginRegistry.plugins)

