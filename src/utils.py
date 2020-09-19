import os
import logging

ROOT = __file__

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S')


def get_full_path(*paths):
    root_dir = os.path.dirname(ROOT)
    full_path = os.path.join(root_dir, *paths)
    return full_path
