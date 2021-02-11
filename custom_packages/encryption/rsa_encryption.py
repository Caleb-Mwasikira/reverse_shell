import os
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15
from Crypto.Cipher import PKCS1_OAEP

from urls.__init__ import KEYS_DIR


class RSAEncryption:
    def __init__(self):
        self.private_key = None
        self.public_key = None

    @staticmethod
    def genKeys():
        print(f"[+] Generating new pair of private and public keys")
        BITS = 2048
        private_key = RSA.generate(BITS)
        public_key = private_key.publickey()
        return private_key, public_key

    @staticmethod
    def pemSaveKey(key, key_file_path, pass_phrase):
        """Saving an encrypted key onto a .pem file"""
        try:
            print(f"[*] Saving encryption key to file")
            keys_folder = os.path.dirname(key_file_path)

            if not os.path.exists(keys_folder):
                os.makedirs(keys_folder)

            with open(key_file_path, "wb+") as f:
                f.write(key.export_key(format="PEM", passphrase=pass_phrase, pkcs=8))
            print(f"[+] Key successfully saved on file {key_file_path}")
            return True

        except FileNotFoundError as err:
            print(f"[-] Error: {err}")

    def pemLoadKey(self, key_file_path, pass_phrase):
        """Importing an encrypted key from a file"""
        try:
            print(f"[*] Loading encryption key from file ...")
            with open(key_file_path, "rb") as f:
                data = f.read()
                key = RSA.import_key(data, passphrase=pass_phrase)

            if key.has_private():  # if key is a private key, generate its corresponding public key
                self.private_key = key
                self.public_key = self.private_key.publickey()

            return key

        except ValueError as error:
            print(f"[-] Error: {error}")
            return False

        except FileNotFoundError as error:
            print(f"[!] Warning : {error}")
            return False

    @staticmethod
    def signMsg(msg, private_key):
        """Signs a message with a private key"""
        signer = pkcs1_15.new(private_key)  # Instantiate a new signer object using the senders private key
        hashed_msg = SHA256.new(msg)
        signature = signer.sign(hashed_msg)
        print(f"[+] Message signed successfully")
        return signature

    @staticmethod
    def verifySignedMsg(msg, signature, public_key):
        """Verifies a signature to see if the message is authentic"""
        try:
            print(f"[*] Verifying message authenticity")
            verifier = pkcs1_15.new(public_key)  # Instantiate a new verifier object using the senders public key
            hashed_msg = SHA256.new(msg)
            verifier.verify(hashed_msg, signature)
            print(f"[+] Message authenticated successfully")
            return True

        except ValueError as error:
            print(f"[-] Error : {error}")
            return False

    @staticmethod
    def encryptMsg(plain_text, public_key):
        try:
            # print(f"[*] Encrypting message")
            if type(plain_text) != bytes:
                plain_text = plain_text.encode("utf-8")

            cipher = PKCS1_OAEP.new(public_key)
            cipher_text = cipher.encrypt(plain_text)
            # print(f"[+] Message encrypted successfully")
            return cipher_text

        except AttributeError as err:
            print(f"[-] Error: {err}")
            return False

    @staticmethod
    def decryptMsg(cipher_text, private_key):
        try:
            # print(f"[*] Decrypting message")
            cipher = PKCS1_OAEP.new(private_key)
            plain_text = cipher.decrypt(cipher_text)
            return plain_text

        except ValueError as error:
            raise Exception(f'Message decryption failed: {error}')


def Main():
    message = b"My deep dark secrets"

    PRIVATE_KEY_FILE = os.path.join(KEYS_DIR, "private_key.pem")
    PUBLIC_KEY_FILE = os.path.join(KEYS_DIR, "public_key.pem")
    PASSWORD = "Sixteen byte keys"  # Just a dummy password used for program testing

    rsa_encryptor = RSAEncryption()
    private_key = rsa_encryptor.pemLoadKey(PRIVATE_KEY_FILE, PASSWORD)

    if private_key:
        public_key = rsa_encryptor.public_key
    else:
        private_key, public_key = rsa_encryptor.genKeys()
        rsa_encryptor.pemSaveKey(private_key, PRIVATE_KEY_FILE, PASSWORD)
        rsa_encryptor.pemSaveKey(public_key, PUBLIC_KEY_FILE, PASSWORD)

    cipher_text = rsa_encryptor.encryptMsg(message, public_key)
    print(cipher_text)

    plain_text = rsa_encryptor.decryptMsg(cipher_text, private_key)
    print(plain_text)

    sig = rsa_encryptor.signMsg(message, private_key)
    rsa_encryptor.verifySignedMsg(message, sig, public_key)


if __name__ == "__main__":
    Main()
