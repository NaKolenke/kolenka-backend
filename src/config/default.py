class Config(object):
    DEBUG = True
    DATABASE = 'sqlite:///database.db'
    PASSWORD_SALT = 'some-salt'
    JSON_AS_ASCII = False
    UPLOAD_FOLDER = 'uploads/'
    HOSTNAME = 'localhost'
    TRELLO_KEY = '<insert_here>'
    TRELLO_TOKEN = '<insert_here>'
    TRELLO_LIST_ID = '<insert_here>'
    GMAIL_SENDER = 'none'
    GMAIL_PASSWORD = 'none'
