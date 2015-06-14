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

    def encrypt(self, plaintext, base64_encode=True, salt=None):

        if (salt is None):
            salt = Crypto.Random.get_random_bytes(self.salt_size)

        key = self.generate_key(salt, self.iterations)
        cipher = AES.new(key, AES.MODE_ECB)
        padded_plaintext = self._pad_text(plaintext)

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
        key = self.generate_key(salt, self.iterations)
        cipher = AES.new(key, AES.MODE_ECB)

        padded_plaintext = cipher.decrypt(ciphertext_sans_salt)

        plaintext = self._unpad_text(padded_plaintext)

        return plaintext.decode("UTF-8")

    def _pad_text(self, text):
        extra_bytes = len(text) % self.aes_multiple
        padding_size = self.aes_multiple - extra_bytes

        padding = chr((padding_size+33)%122) * padding_size
        padded_text = text + padding

        return padded_text

    def _unpad_text(self, padded_text):
        last_char = padded_text[len(padded_text)-1]
        if (isinstance(last_char, str)):
            last_char = ord(last_char)
        padding_size = (last_char)-33
        text = padded_text[:-padding_size]

        return text

    def generate_key(self, salt, iterations):
        assert iterations > 0
        key = self.password.encode('UTF-8') + salt

        for i in range(iterations):
            key = hashlib.sha256(key).digest()

        return key


