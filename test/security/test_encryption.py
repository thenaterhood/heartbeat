import unittest
import sys
if (sys.version_info < (3, 3)):
    from mock import MagicMock
    from mock import Mock
else:
    from unittest.mock import MagicMock
    from unittest.mock import Mock
from heartbeat.security import Encryptor


class EncryptorTest(unittest.TestCase):

    def setUp(self):
        self.password = 'foo_bar'
        self.encryptor = Encryptor(self.password)

    def test_init(self):
        """
        Encryptor can be instantiated
        """
        e = Encryptor(self.password)

        self.assertEqual(e.password, self.password)

    def test_pad_text(self):
        """
        Encryptor correctly pads short text
        """
        text = 'foo_bar'

        padded_text = self.encryptor._pad_text(text)
        self.assertEqual(len(padded_text), self.encryptor.aes_multiple)
        self.assertEqual(padded_text, 'foo_bar*********')

    def test_pad_text_long(self):
        """
        Encryptor correctly pads long text (len between multiples of 16)
        """
        text = 'foo_bar_foo_bar_foo_bar'

        padded_text = self.encryptor._pad_text(text)
        self.assertEqual(len(padded_text), 32)
        self.assertEqual(padded_text, 'foo_bar_foo_bar_foo_bar*********')

    def test_unpad_text(self):
        """
        Encryptor correctly removes padding from text
        """
        padded_text = 'foo_bar*********'

        unpadded_text = self.encryptor._unpad_text(padded_text)
        self.assertEqual(unpadded_text, 'foo_bar')

    def test_generate_key(self):
        """
        Encryptor correctly generates keys from the password
        """
        correct_key = b'\x1b\x95\xf2\xd9j|\xf7\xff\xbc\x1f\xdb\xe2\xb2\xe6\x82\rq\xd9\xdf4\xbc\xad3\xa1P\xe8\xe8\xab.\xfc\x8f\xa2'

        key = self.encryptor.generate_key(b'heartbeat', 20)
        self.assertEqual(key, correct_key)

    def test_encrypt(self):
        """
        Encryptor correctly encrypts text
        """
        plaintext = 'test_text'
        correct_encrypted = b'aGVhcnRiZWF0aGVhcnRiZd5sZecsTA83iQ5TDpvJ65w='

        encrypted = self.encryptor.encrypt(plaintext, True, b'heartbeatheartbe')
        self.assertEqual(encrypted, correct_encrypted)

    def test_encrypt_16(self):
        """
        Strings requiring 0 padding are encrypted correctly
        """
        plaintext = 'test_text_16_now'
        correct_encrypted = b'aGVhcnRiZWF0aGVhcnRiZct2fh0EhS3LRnxKJkFWsdFG9+RffOSPDIzvndEoNGfZ'
        encrypted = self.encryptor.encrypt(plaintext, True, b'heartbeatheartbe')

        self.assertEqual(encrypted, correct_encrypted)

    def test_decrypt(self):
        """
        Encryptor correctly decrypts text
        """
        correct_plaintext = 'test_text'
        encrypted = b'aGVhcnRiZWF0aGVhcnRiZd5sZecsTA83iQ5TDpvJ65w='

        plaintext = self.encryptor.decrypt(encrypted, True)
        self.assertEqual(plaintext, correct_plaintext)

    def test_decrypt_16(self):
        """
        Strings requiring 0 padding are decrypted correctly
        """
        correct_plaintext = 'test_text_16_now'
        encrypted = b'aGVhcnRiZWF0aGVhcnRiZct2fh0EhS3LRnxKJkFWsdFG9+RffOSPDIzvndEoNGfZ'
        plaintext = self.encryptor.decrypt(encrypted, True)
        self.assertEqual(plaintext, correct_plaintext)
