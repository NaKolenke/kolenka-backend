from peewee import *

db = None

def init_database():
    db = SqliteDatabase('database.db')

def get_database():
    if not db:
        init_database()
    return db
