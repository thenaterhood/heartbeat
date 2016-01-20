import Crypto.Random
from Crypto.Cipher import AES
import hashlib
import base64


class Encryptor(object):

    """
    Encryptor class to handle encrypting and decrypting
    of strings
    """

    def __init__(self, password):
        """
        Constructor. Accepts a password to
        use for encryption as a parameter and
        sets other encryption defaults.

        Parameters:
            string password: encryption password
        """

        self.password = password
        self.salt_size = 16
        self.iterations = 20
        self.aes_multiple = 16

    def encrypt(self, plaintext, base64_encode=True, salt=None):
        """
        Encrypts a plaintext string and returns it

        Parameters:
            string plaintext: A plaintext string to encrypt
            bool   base64_encode: whether to return the encrypted
                        string in base64 encoding. Default true.
            bytes  salt: A salt. Generated randomly if unspecified or None

        Returns:
            bytes: an encrypted, salted string
        """

        if (salt is None):
            salt = Crypto.Random.get_random_bytes(self.salt_size)

        key = self.generate_key(salt, self.iterations)
        cipher = AES.new(key, AES.MODE_ECB)
        padded_plaintext = self._pad_text(plaintext)

        ciphertext = cipher.encrypt(padded_plaintext.encode("UTF-8"))
        ciphertext_with_salt = salt + ciphertext

        if (base64_encode):
            return base64.b64encode(ciphertext_with_salt)
        else:
            return ciphertext_with_salt

    def decrypt(self, ciphertext, base64_encoded=True):
        """
        Decrypts an encrypted string to plaintext and returns it

        Parameters:
            bytes ciphertext: an encrypted string
            bool  base64_encoded: whether the ciphertext is base64 encoded.
                    Defaults to true.

        Returns:
            string: The decrypted string
        """

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
        """
        Pads text out to the proper length for AES encryption.
        The method will choose the character to use for padding
        based on how much padding is necessary.

        Parameters:
            string text: the plaintext string to pad

        Returns:
            string: the padded string
        """

        extra_bytes = len(text) % self.aes_multiple
        padding_size = self.aes_multiple - extra_bytes

        padding = chr((padding_size + 33) % 122) * padding_size
        padded_text = text + padding

        return padded_text

    def _unpad_text(self, padded_text):
        """
        Removes padding from a plaintext string. The method will
        determine the padding from the last character in the string
        and use its ord to determine the number of padding to
        remove.

        Parameters:
            string padded_text: A padded string

        Returns:
            string: the unpadded text
        """

        last_char = padded_text[len(padded_text) - 1]
        if (isinstance(last_char, str)):
            last_char = ord(last_char)
        padding_size = (last_char) - 33
        text = padded_text[:-padding_size]

        return text

    def generate_key(self, salt, iterations):
        """
        Generates an encryption key

        Parameters:
            bytes salt: a salt to use for the encryption
            int   iterations: the number of iterations of encryption

        Returns:
            bytes: the encryption key
        """

        assert iterations > 0
        key = self.password.encode('UTF-8') + salt

        for i in range(iterations):
            key = hashlib.sha256(key).digest()

        return key
