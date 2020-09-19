from pymongo import MongoClient
from src.database.clients.config import Config
import logging


class Connector(Config, MongoClient):
    def __init__(self):
        super().__init__()
        self.MongoClient = MongoClient
        self.host = Config.HOST
        self.port = Config.PORT
        self.db = Config.DB
        self.user = Config.AUTH_USER
        self.password = Config.PASS

    def connection_maker(self):
        try:
            client = self.MongoClient(f"mongodb://{self.user}:{self.password}@{self.host}/{self.db}",
                                      serverSelectionTimeoutMS=2000,
                                      maxPoolSize=None)
            status = client.server_info()['ok']
            db_connection = client[self.db]
            logging.info(f'Connection created Successfully! ["Status":{status}]')
            return db_connection
        except Exception as error:
            logging.error(f'in Creating connection ! {error}')
