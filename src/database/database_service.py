from src.database.clients.connector import Connector
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError, BulkWriteError
import datetime
import logging


class Category(Connector):
    def __init__(self):
        super().__init__()

    def get_category(self):
        pass

    def add_category(self, data):
        db_con = self.connection_maker()
        try:
            result = db_con['rank_list_category'].insert_one({'name': data})
            logging.info(f'New Category inserted _id ==> ({result.inserted_id})')
            logging.info(f'Total Categories ==> {db_con["rank_list_category"].count_documents({})}')
        except DuplicateKeyError:
            logging.warning(f'Category already exists!')
        except Exception as error:
            logging.error(f'in Inserting new category! {error}')


class RankedList(Connector):
    def __init__(self):
        super().__init__()

    def get_ranked_list(self):
        pass

    def add_ranked_list(self, data):
        db_con = self.connection_maker()
        try:
            cat_id = db_con['rank_list_category'].find_one({'name': data['category']})['_id']
            only_rank_list = data.copy()
            only_rank_list.pop('ranked_items', None)
            only_rank_list['category_id'] = ObjectId(cat_id)
            result = db_con['rank_lists'].insert_one(only_rank_list)
            logging.info(f'Ranked list inserted _id ==> ({result.inserted_id})')
        except DuplicateKeyError:
            logging.warning(f'Ranked List already exists!')
        except Exception as error:
            logging.error(f'in Inserting new Ranked list! {error}')
        logging.info(f'Total Ranked list ==> {db_con["rank_lists"].count_documents({})}')


class RankedItem(Connector):
    def __init__(self):
        super().__init__()

    def get_ranked_item(self):
        pass

    def add_ranked_item(self, ranked_item, list_title):
        db_con = self.connection_maker()
        list_title_id = db_con['rank_lists'].find_one({"list_title": list_title})['_id']
        try:
            only_rank_item = ranked_item.copy()
            only_rank_item['list_id'] = ObjectId(list_title_id)
            only_rank_item['updated_at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            only_rank_item['created at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            only_rank_item['sync'] = False
            result = db_con['ranked_item'].insert_one(only_rank_item)
            logging.info(f'Ranked item inserted _id ==> ({result.inserted_id})')
        except DuplicateKeyError:
            logging.warning(f'Ranked Item already exists!')
        except Exception as error:
            logging.error(f'in Inserting new category! {error}')
        logging.info(f'Total Ranked item ==> {db_con["ranked_item"].count_documents({})}')

    def add_multiple_ranked_items(self, ranked_item_list, list_title):
        db_con = self.connection_maker()
        list_title_id = db_con['rank_lists'].find_one({"list_title": list_title})['_id']
        insert_many_dicts = []
        for ranked_item in ranked_item_list:
            try:
                only_rank_item = ranked_item.copy()
                only_rank_item['list_id'] = ObjectId(list_title_id)
                only_rank_item['updated_at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                only_rank_item['created at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                only_rank_item['sync'] = False
                insert_many_dicts.append(only_rank_item)
            except KeyError:
                print('KeyError here')
            except Exception as error:
                logging.error(f'in creating list of dict Item! {error}')
        try:
            result = db_con['ranked_item'].insert_many(insert_many_dicts, ordered=False,
                                                       bypass_document_validation=True)
            logging.info(f'Ranked item inserted _id Many1 ==> ({result.inserted_ids})')
        except BulkWriteError:
            logging.warning(f'Some Ranked Item already exists Many!')
        except Exception as error:
            logging.error(f'in Inserting new Item Many! {error}')
        logging.info(f'Total Ranked item ==> {db_con["ranked_item"].count_documents({})}')
