import Crypto.Random
from Crypto.Cipher import AES
import hashlib
import base64

class Encryptor():

    def __init__(self, password):
        self.password = password
        self.salt_size = 16
        self.iterations = 20
        self.aes_multiple = 16

    def encrypt(self, plaintext, base64_encode=True):

        salt = Crypto.Random.get_random_bytes(self.salt_size)
        key = self.generate_key(password, salt, self.iterations)
        cipher = AES.new(key, AES.MODE_ECB)
        padded_plaintext = self._pad_text(plaintext, AES_MULTIPLE)

        ciphertext = cipher.encrypt(padded_plaintext)
        ciphertext_with_salt = salt + ciphertext

        if (base64_encode):
            return base64.b64encode(ciphertext_with_salt)
        else:
            return ciphertext_with_salt

    def decrypt(self, ciphertext, base64_encoded=True):

        if (base64_encoded):
            ciphertext = base64.b64decode(ciphertext)

        salt = ciphertext[0:self.salt_size]
        ciphertext_sans_salt = ciphertext[self.salt_size:]
        key = self.generate_key(self.password, salt, self.iterations)
        cipher = AES.new(key, AES.MODE_ECB)

        padded_plaintext = cipher.decrypt(ciphertext_sans_salt)

        plaintext = self._unpad_text(padded_plaintext)

        return plaintext

    def _pad_text(self, text):
        extra_bytes = len(text) % multiple
        padding_size = multiple - extra_bytes

        padding = chr(padding_size) * padding_size
        padded_text = text + padding

        return padded_text

    def _unpad_text(self, padded_text):
        padding_size = ord(padded_text[-1])
        text = padded_text[:-padding_size]

        return text

    def generate_key(password, salt, iterations):
        assert iterations > 0
        key = password + salt

        for i in range(iterations):
            key = hashlib.sha256(key).digest()

        return key


