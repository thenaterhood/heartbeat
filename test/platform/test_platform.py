import unittest
import sys
import json
import pymlconf
from heartbeat.platform import Event
from heartbeat.platform import _translate_legacy_config
from heartbeat.platform import get_config_manager

class EventTest(unittest.TestCase):

    def setUp(self):
        self.event = Event('Titanium Message', 'a message from titanium', 'titanium')
        self.event.source = 'test'

    def test_basic_instantiate(self):
        event = Event()
        self.assertEqual('', event.title)
        self.assertEqual('', event.message)
        self.assertEqual('localhost', event.host)

    def test_std_instantiate(self):
        host = 'titanium'
        message = 'a message from titanium'
        title = 'Titanium Message'

        event = Event(title, message, host)

        self.assertEqual(host, event.host)
        self.assertEqual(message, event.message)
        self.assertEqual(title, event.title)

    def test_hash(self):
        self.assertEqual(self.event.__hash__(), self.event.__hash__())
        e = Event()
        self.assertNotEqual(e.__hash__(), self.event.__hash__())


    def test_json_dump(self):
        event_json = self.event.to_json()

        as_dict = json.loads(event_json)

        self.assertEqual(self.event.title, as_dict['title'])
        self.assertEqual(self.event.message, as_dict['message'])

    def test_json_load(self):
        event_json = self.event.to_json()

        e = Event()
        e.load_json(event_json)

        self.assertEqual(self.event.__hash__(), e.__hash__())

class ConfigTest(unittest.TestCase):

    def setUp(self):
        self.config_file = 'test/heartbeat.yml'

    def test_legacy_config(self):
        conf = _translate_legacy_config(self.config_file, {'heartbeat': {}, 'monitoring': {}, 'notifying': {}})
        print(conf)
        self.assertTrue('heartbeat' in conf)
        self.assertEqual(conf['heartbeat']['secret_key'], 'heartbeat3477')

        self.assertTrue('monitoring' in conf)
        self.assertEqual(conf['monitoring']['smartctl']['drives'][0], '/dev/sda')

        self.assertTrue('notifying' in conf)
        self.assertEqual(conf['notifying']['pushbullet']['api_keys'][0], 'api_key_1')

    def test_config(self):
        conf = get_config_manager('dist/_etc/heartbeat')
        self.assertEqual(conf.heartbeat.secret_key, 'heartbeat3477')
        self.assertEqual(conf.heartbeat.port, 21999)
        self.assertEqual(conf.notifying.pushbullet.api_keys, ['api_key_1', 'api_key_2'])

