class TestConfig(object):
    DEBUG = True
    DATABASE_FOR_REMOVE = 'testdb.db'
    DATABASE = 'sqlite:///' + DATABASE_FOR_REMOVE
