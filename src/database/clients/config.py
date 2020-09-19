import os


class Config:
    HOST = os.environ.get('HOST')
    DB = os.environ.get('DB')
    PORT = int(os.environ.get('PORT'))
    AUTH_USER = os.environ.get('AUTH_USER')
    PASS = os.environ.get('PASS')
