import redis
import toml
import hashlib
import json
from uuid import uuid4

from urls.__init__ import ROOT


class RedisDatabase:
    def __init__(self, db_config):
        self.r = self.connectToDatabase(
            db_config['HOST'], db_config['PORT'],
            db_config['DATABASE'], db_config['PASSWORD']
        )

    @staticmethod
    def connectToDatabase(HOST, PORT, DB, PASSWORD):
        print(f"[*] Connecting to a redis database")
        r = redis.Redis(
            host=HOST, port=PORT,
            db=DB, password=PASSWORD
        )
        # print(f"[+] Successfully connected to redis database")
        return r

    def createNewUser(self, user: dict):
        user_id, user_name = user['user_id'], user['user_name']
        user: str = json.dumps(user)

        try:
            self.r.set(f"user:{user_name}", user)
            print(f"[+] Created new user with alias: '{user_name}' @ id: {user_id}")
            return True

        except redis.exceptions.RedisError as err:
            print(f"[-] Error: {err}")
            return False

    def selectExistingUser(self, user_name):
        try:
            db_result: bytes = self.r.get(f"user:{user_name}")

            if db_result:
                user: dict = json.loads(db_result)
                print(f"[+] Fetched user: '{user_name}' id: {user['user_id']} from database")
                return user
            return False

        except redis.exceptions.RedisError as err:
            print(f"[-] Error: {err}")
            return False

    def deleteExistingUser(self, user_name):
        try:
            db_result: bytes = self.r.delete(f"user:{user_name}")

            if db_result:
                print(f"[+] User: '{user_name}' successfully DELETED from database")
                return True

            print(f"[-] User '{user_name}' DOES NOT EXIST in database")
            return False

        except redis.exceptions.RedisError as err:
            print(f"[-] Error: {err}")
            return False


def readConfigFile(config_filepath=fr'{ROOT}/settings/config.toml'):
    config = toml.load(config_filepath)
    return config


def Main():
    # Example user object
    user = dict(
        user_id= str(uuid4())[:8],
        user_name= "John Doe",
        user_password= hashlib.sha3_256("password".encode('utf-8')).hexdigest()[:12]
    )
    db_config = readConfigFile()['REDIS-DATABASE']
    redis_database = RedisDatabase(db_config)

    redis_database.createNewUser(user)
    db_user: dict = redis_database.selectExistingUser(user['user_name'])
    print(db_user)
    # redis_database.deleteExistingUser(user['user_name'])



if __name__ == "__main__":
    Main()