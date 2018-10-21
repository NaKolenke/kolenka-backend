from peewee import *

db = None

def init_database():
    global db
    if db is None:
        db = SqliteDatabase('database.db')
        db.connect()

def create_tables():
    global db
    from src.model.user import User
    db.create_tables([User])

    User.create(name="Test")

def get_database():
    global db
    if db is None:
        init_database()
    return db
