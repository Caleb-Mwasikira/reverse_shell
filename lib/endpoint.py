import toml
import logging
import pickle
import colorama as colors

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
        # keys_conf, redis_db_conf = config['KEYS'], config['REDIS-DATABASE']

        # Ready log books
        log_filename = fr"{ROOT}/logs/log_book.log"
        self.logger = self.readyLogBooks(log_filename)

        self.HOST = project_conf['HOST']
        self.PORT = project_conf['PORT']


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

        if data:
            _socket.send(data)
            print(f"[+] Msg sent successfully")
            return True
        else:
            raise Exception('Message encryption failed')

    def receiveMsg(self, _socket):
        BYTES = 1024
        data: bytes = _socket.recv(BYTES)

        print(f"\n[+] Msg received from {self.HOST}:{self.PORT}")


        if data:
            data: dict = pickle.loads(data)
            return data

        else:
            raise Exception('No message received')

    def closeConnection(self, socket, HOST, PORT):
        message = f"Closing connection with {HOST}:{PORT}. Connection aborted."
        socket.close()
        self.logger.info(message)
        print(f"[+] {message}")