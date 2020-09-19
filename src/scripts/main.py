from src import utils
import logging

if __name__ == "__main__":
    try:
        from src.scripts import get_items_list
        get_items_list.crawler()
        logging.info('Crawling Done Successfully !!!')
    except:
        raise Exception('Error! in main.py!!!')

