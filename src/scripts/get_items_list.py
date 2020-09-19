import threading
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from src import utils
import logging
import random
from src.lists import genres, user_agents, links_list
from src.database.database_service import Category, RankedList, RankedItem
from pyvirtualdisplay import Display
from src.database.clients.index_creater import IndexCreator

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-impl-side-painting")
options.add_argument("--disable-setuid-sandbox")
options.add_argument("--disable-seccomp-filter-sandbox")
options.add_argument("--disable-breakpad")
options.add_argument("--disable-client-side-phishing-detection")
options.add_argument("--disable-cast")
options.add_argument("--disable-cast-streaming-hw-encoding")
options.add_argument("--disable-cloud-import")
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--ignore-certificate-errors")
options.add_argument("--disable-session-crashed-bubble")
options.add_argument("--disable-ipv6")
options.add_argument("--allow-http-screen-capture")
options.add_argument("--start-maximized")

prefs = {
    "translate_whitelists": {"fr": "en", "de": "en", 'it': 'en', 'no': 'en', 'es': 'en', 'sv': 'en', 'nl': 'en',
                             'da': 'en', 'pl': 'en', 'fi': 'en', 'cs': 'en'},
    "translate": {"enabled": "true"}
}
options.add_experimental_option("prefs", prefs)
display = Display(visible=0)
display.start()


class ItemListGetter:
    imdb_list = []

    def __init__(self, record, category, subcategory=None):
        if subcategory is None:
            subcategory = []
        self.items_url = record
        self.imdb_single_url = {"list_title": "",
                                "list_url": self.items_url,
                                "no_of_items": 0,
                                "category": category,
                                "subcategory": subcategory,
                                "source": "https://www.imdb.com/",
                                "ranked_items": []}
        user_agent = random.choice(user_agents)
        logging.info(f'User Agent ==> {user_agent}')
        options.add_argument(f'user-agent={user_agent}')
        self.driver = webdriver.Chrome(options=options)

    def __del__(self):
        logging.info("Delete")

    def start(self):
        logging.info("Start")
        self.sequence_caller()

    def start_genres(self):
        logging.info("Start")
        self.genres_sequence_caller()

    def get_list_title(self):
        try:
            item_list_title: WebElement = self.driver.find_element_by_css_selector('h1.header').text
            title_str = str(str(item_list_title).strip().lower())
            self.imdb_single_url['list_title'] = title_str
            logging.info(f"Items List title ==> {title_str}")
        except Exception as error:
            logging.error(f"in getting Items List Title ==> {error}")
            self.driver.quit()
            self.__del__()

    def get_items_list(self, selector):
        try:
            sleep(2)
            list_items = self.driver.find_elements_by_css_selector(selector)
            logging.info(f'Items List Length ==> {len(list_items)}')
            self.imdb_single_url['no_of_items'] = len(list_items)
            for i, item in enumerate(list_items):
                try:
                    item_source_link = item.get_attribute('href')
                    item = {"rank": int(i + 1), "title": "", "location": "", "details": "", "country": "", "image": "",
                            "link": item_source_link}
                    self.imdb_single_url['ranked_items'].append(item)
                except Exception as error:
                    logging.error(f"Error in extracting source link==> {error}")
        except Exception as error:
            logging.error(f"in getting Items List ==> {error}")
            self.driver.quit()

    def insert_into_db(self):

        cat = Category()
        cat.add_category(self.imdb_single_url['category'])

        ranked_list = RankedList()
        ranked_list.add_ranked_list(self.imdb_single_url)

    def sequence_caller(self):
        try:
            logging.info(f"Getting Items from URL ==> {self.items_url}")
            self.driver.get(self.items_url)
            self.get_list_title()
            sleep(2)
            self.driver.execute_script("window.scrollTo(0, 2000)")
            sleep(2)
            self.get_items_list('.titleColumn a')
            if len(self.imdb_single_url['ranked_items']):
                self.imdb_list.append(self.imdb_single_url)
                self.insert_into_db()

            self.driver.quit()

        except Exception as error:
            logging.error(f"in getting Item list page ==> {error}")

    def genres_sequence_caller(self):
        try:
            logging.info(f"Getting Items for URL ==> {self.items_url}")
            self.driver.get(self.items_url)
            self.get_list_title()
            sleep(2)
            self.driver.execute_script("window.scrollTo(0, 2000)")
            sleep(2)
            self.get_items_list('.lister-item-header a')
            if len(self.imdb_single_url['ranked_items']):
                self.imdb_list.append(self.imdb_single_url)
                self.insert_into_db()
            self.driver.quit()
        except Exception as error:
            logging.error(f"Error in getting genres(self created links) Item list page ==> {error}")


class ItemsDetailGetter:
    def __init__(self):
        pass

    def start(self):
        logging.info("Start Getting details...")
        self.get_item_details()

    @staticmethod
    def insert_item(arg_ranked_item, list_title):
        ranked_item = RankedItem()
        ranked_item.add_ranked_item(arg_ranked_item, list_title)

    def get_item_details(self):
        for bt_url in ItemListGetter.imdb_list:
            for i in range(0, len(bt_url['ranked_items']), 1):
                all_t = []
                twenty_records = bt_url['ranked_items'][i:i + 1]
                for ranked_item in twenty_records:
                    try:
                        t = threading.Thread(target=self.get_item_details_onpage,
                                             args=(ranked_item, bt_url['list_title']))
                        t.start()
                        all_t.append(t)
                    except Exception as error:
                        logging.error(f"Error in starting thread ==> {error}")
                for count, t in enumerate(all_t):
                    logging.info(f" joining Thread no ==> {count}")
                    t.join()

    def get_item_details_onpage(self, ranked_item, list_title):
        user_agent = random.choice(user_agents)
        logging.info(f'User Agent ==> {user_agent}')
        options.add_argument(f'user-agent={user_agent}')
        driver_inner = webdriver.Chrome(options=options)
        try:
            driver_inner.get(ranked_item['link'])
            logging.info(f"Getting details from URL ==> {ranked_item['link']}")
            sleep(2)
        except Exception as error:
            logging.error(f"Error in getting Details page ==> {error}")
            driver_inner.quit()

        try:
            ranked_item_title: WebElement = driver_inner.find_element_by_css_selector('.title_wrapper h1').text
            ranked_item['title'] = ranked_item_title

            driver_inner.execute_script("window.scrollTo(0, 2000)")
        except Exception as error:
            logging.error(f'in getting Ranked Item Title {error}')
            driver_inner.quit()
        try:
            ranked_item_details: WebElement = driver_inner.find_element_by_css_selector('div#titleDetails').text
            try:
                ranked_item['country'] = str(ranked_item_details).split('Country:')[1].split('\n')[0].strip()
            except IndexError as error:
                logging.warning(f'in getting Ranked Item country {error}')

            try:
                ranked_item['location'] = str(ranked_item_details).split('Locations:')[1].split('\n')[0].strip(
                    'See more »')
            except IndexError as error:
                logging.warning(f'in getting Ranked Item location {error}')
        except Exception as error:
            logging.error(f'in getting Ranked Item Details contain location etc {error}')

        try:
            sleep(2)
            ranked_item['image'] = driver_inner.find_element_by_css_selector('.poster img').get_attribute("src")
        except Exception as error:
            logging.error(f'in getting Ranked Item Image {error}')

        try:
            ranked_item_details: WebElement = driver_inner.find_element_by_css_selector('p span').text
            ranked_item['details'] = ranked_item_details
        except Exception as error:
            logging.error(f'in getting Ranked Item Details {error}')
        driver_inner.quit()
        self.insert_item(ranked_item, list_title)


def crawler():
    IndexCreator()
    for record_arg in links_list:
        ilg = ItemListGetter(record_arg['url'], record_arg['category'])
        ilg.start()

    for genre in genres:
        for genre_2 in genres:
            try:
                link = f'https://www.imdb.com/search/title/?genres={genre}&genres={genre_2}&ref_=adv_explore_rhs'
                gilg = ItemListGetter(link, category='movies and tv shows', subcategory=[genre, genre_2])
                gilg.start_genres()
            except Exception as error:
                logging.error(f'in getting Ranked list Genre {error}')

    idg = ItemsDetailGetter()
    idg.start()
    display.stop()


if __name__ == "__main__":
    crawler()
