from src.database.clients.connector import Connector
import logging


class IndexCreator(Connector):
    INDEXED = False

    def __init__(self):
        super().__init__()
        self.create_index()

    def create_index(self):
        try:
            db_con = self.connection_maker()
            db_con['rank_list_category'].create_index('name', unique=True)
            db_con['rank_lists'].create_index('list_title', unique=True)
            db_con['rank_lists'].create_index('category_id')
            db_con['ranked_item'].create_index([('title', 1), ('list_id', -1)], unique=True)
            self.INDEXED = True
            logging.info(f'Index Created!')
        except Exception as error:
            logging.error(f'Index Already Exists! {error}')
