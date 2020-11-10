import toml
import logging
import os
import pickle
import colorama as colors
from getpass import getpass
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from encryption.rsa_encryption import RSAEncryption
from urls.__init__ import ROOT


class EndPoint:
    def __init__(self):
        # Initialise colorama; beautiful colors on he terminal
        colors.init()
        self.colors_SUCCESS = colors.Fore.GREEN
        self.colors_FAIL = colors.Fore.RED
        self.colors_PRIMARY = colors.Fore.MAGENTA
        self.colors_RESET = colors.Style.RESET_ALL

        # Read config file
        conf_filename = fr"{ROOT}/settings/config.toml"
        config = self.readConfigFile(conf_filename)
        self.app_conf, project_conf = config['APP'], config['PROJECT']
        keys_conf, redis_db_conf = config['KEYS'], config['REDIS-DATABASE']

        # Ready log books
        log_filename = fr"{ROOT}/logs/log_book.log"
        self.logger = self.readyLogBooks(log_filename)

        self.HOST = project_conf['HOST']
        self.PORT = project_conf['PORT']

        # Initialise RSA encryption
        self.rsa_encryptor, self.private_key, self.public_key = self.initRSAEncryption(keys_conf)

        # AES encryption
        self.AES_KEY = None
        self.AES_IV = None

    @staticmethod
    def initRSAEncryption(keys_conf):
        print(f"[*] Setting up a secure connection")
        private_key_file: str = os.path.join(ROOT, keys_conf['PRIVATE_KEY_FILE'])
        public_key_file: str = os.path.join(ROOT, keys_conf['PUBLIC_KEY_FILE'])
        password: str = keys_conf['PASSWORD']

        while password is None:
            password = getpass(prompt="Please enter your password to continue >> ")
            if len(password) >= 6:
                break
            else:
                print(f"[!] Password not secure")

        rsa_encryptor = RSAEncryption()
        private_key = rsa_encryptor.pemLoadKey(private_key_file, password)

        if private_key:
            public_key = rsa_encryptor.public_key

        else:
            private_key, public_key = rsa_encryptor.genKeys()
            rsa_encryptor.pemSaveKey(private_key, private_key_file, password)
            rsa_encryptor.pemSaveKey(public_key, public_key_file, password)

        return rsa_encryptor, private_key, public_key

    @staticmethod
    def initAESEncryption(key: bytes, iv: bytes = None):
        key_size = 16
        iv_size = 16
        AES_KEY = key[:key_size] if len(key) > key_size else pad(key, key_size)
        AES_IV = iv or os.urandom(iv_size)
        assert(len(AES_KEY) == key_size)  # key must a be 8, 16, 32 byte key
        assert(len(AES_IV) == iv_size)  # initialization vector must be 16 bytes long
        return AES_KEY, AES_IV

    @staticmethod
    def readConfigFile(conf_filename):
        config = toml.load(conf_filename)
        return config

    @staticmethod
    def readyLogBooks(log_filename):
        LOG_FORMAT = "%(levelname)s : %(asctime)s - %(message)s"
        logging.basicConfig(
            filename=log_filename,
            level=logging.DEBUG,
            format=LOG_FORMAT
        )
        return logging.getLogger()

    def sendMsg(self, _socket, msg: dict):
        print(f"[*] Sending msg to {self.HOST}:{self.PORT}")
        data: bytes = pickle.dumps(msg)

        if self.AES_KEY and self.AES_IV:
            cipher = AES.new(self.AES_KEY, AES.MODE_CBC, self.AES_IV)
            cipher_text = cipher.encrypt(pad(data, AES.block_size))
        else:
            cipher_text = self.rsa_encryptor.encryptMsg(data, self.public_key)

        if cipher_text:
            _socket.send(cipher_text)
            print(f"[+] Msg sent successfully")
            return True
        else:
            raise Exception('Message encryption failed')


    def receiveMsg(self, _socket):
        BYTES = 1024
        encrypted_data: bytes = _socket.recv(BYTES)

        if encrypted_data:
            print(f"\n[+] Msg received from {self.HOST}:{self.PORT}")

            if self.AES_KEY and self.AES_IV:
                cipher = AES.new(self.AES_KEY, AES.MODE_CBC, self.AES_IV)
                plain_text = unpad(cipher.decrypt(encrypted_data), AES.block_size)
            else:
                plain_text = self.rsa_encryptor.decryptMsg(encrypted_data, self.private_key)

            if plain_text:
                data: dict = pickle.loads(plain_text)
                return data

            else:
                raise Exception('Failed to decrypt encrypted message')
        else:
            raise ConnectionResetError("No data received from endpoint. Current connection might be down")


    def closeConnection(self, socket, HOST, PORT):
        message = f"Closing connection with {HOST}:{PORT}. Connection aborted."
        socket.close()
        self.logger.info(message)
        print(f"[+] {message}")