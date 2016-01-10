import unittest
import sys
from heartbeat.plugin import ModuleLoader

class ModuleLoaderTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_load_path(self):
        """
        ModuleLoader correctly imports a path
        """
        # This is a tainted test because it does not
        # mock everything involved.

        ModuleLoader.load('heartbeat.notifications')
        self.assertTrue('heartbeat.notifications' in sys.modules)

    def test_load_bad_path(self):
        """
        ModuleLoader correctly throws an error on importing a bad path
        """
        self.assertRaises(ImportError, lambda: ModuleLoader.load('foo.bar'))

