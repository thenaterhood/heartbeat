import unittest
import sys
from heartbeat.plugin import Plugin, PluginRegistry


class TestPluginRegistry(unittest.TestCase):

    def setUp(self):
        PluginRegistry._PluginRegistry__whitelist = []

    def tearDown(self):
        PluginRegistry._PluginRegistry__whitelist = []
        PluginRegistry._PluginRegistry__plugins = []
        PluginRegistry._PluginRegistry__active_plugins = []
        PluginRegistry._PluginRegistry__available_services = []

    def test_auto_register(self):
        """
        Class inheriting from Plugin is correctly registered
        """

        PluginRegistry._PluginRegistry__whitelist.append("plugin.test_pluginregistry.MockPlugin")
        class MockPlugin(Plugin):
            """
            Fake plugin class to make sure importing operates
            correctly
            """
            pass

        self.assertTrue(MockPlugin in PluginRegistry._PluginRegistry__plugins)

    def test_auto_register_not_whitelisted(self):
        """
        Class inheriting from Plugin is ignored if not in whitelist
        """

        class MockPlugin(Plugin):
            """
            Fake plugin class
            """
            pass

        self.assertFalse(MockPlugin in PluginRegistry._PluginRegistry__plugins)

    def test_populate_whitelist(self):
        """
        Whitelist is properly populated only once
        """

        whitelist = ["plugin.test_pluginregistry.MockPlugin"]
        PluginRegistry.populate_whitelist(whitelist)

        self.assertEqual(whitelist, PluginRegistry._PluginRegistry__whitelist)

        self.assertRaises(Exception, lambda: PluginRegistry.populate_whitelist(whitelist))

        class MockPlugin(Plugin):
            """
            Fake plugin class
            """
            pass

        self.assertTrue(MockPlugin in PluginRegistry._PluginRegistry__plugins)

    def test_simple_activate_plugins(self):

        whitelist = [
                'plugin.test_pluginregistry.MockPlugin1',
                'plugin.test_pluginregistry.MockPlugin2'
                ]


        PluginRegistry.populate_whitelist(whitelist)

        class MockPlugin1(Plugin):
            pass

        class MockPlugin2(Plugin):
            pass

        PluginRegistry.activate_plugins()
        self.assertTrue(len(PluginRegistry._PluginRegistry__active_plugins) == 2)

    def test_activate_with_deps(self):

        PluginRegistry._PluginRegistry__whitelist = []
        whitelist = [
                'plugin.test_pluginregistry.MockPluginDeps1',
                'plugin.test_pluginregistry.MockPluginDeps2'
                ]

        PluginRegistry.populate_whitelist(whitelist)

        class MockPluginDeps1(Plugin):
            def get_services(self):
                return ['foobar']

        class MockPluginDeps2(Plugin):
            def get_required_services(self):
                return ['foobar']

        PluginRegistry.activate_plugins()
        self.assertTrue(len(PluginRegistry._PluginRegistry__active_plugins) == 2)

    def test_activate_with_deps_out_of_order(self):

        PluginRegistry._PluginRegistry__whitelist = []
        whitelist = [
                'plugin.test_pluginregistry.MockPluginDeps1',
                'plugin.test_pluginregistry.MockPluginDeps2'
                ]

        PluginRegistry.populate_whitelist(whitelist)

        class MockPluginDeps2(Plugin):
            def get_required_services(self):
                return ['foobar']

        class MockPluginDeps1(Plugin):
            def get_services(self):
                return ['foobar']

        PluginRegistry.activate_plugins()
        self.assertTrue(len(PluginRegistry._PluginRegistry__active_plugins) == 2)

    def test_activate_with_bad_deps(self):

        whitelist = [
                'plugin.test_pluginregistry.MockPlugin1',
                'plugin.test_pluginregistry.MockPlugin2',
                ]

        PluginRegistry.populate_whitelist(whitelist)

        class MockPlugin1(Plugin):
            def get_services(self):
                return ['foobar']

        class MockPlugin2(Plugin):
            def get_required_services(self):
                return ['barbaz']

        PluginRegistry.activate_plugins()

        self.assertEqual(len(PluginRegistry._PluginRegistry__active_plugins), 1)
