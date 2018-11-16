from peewee import *
from src.model import db

class User(db.db_wrapper.Model):
    login = CharField(unique=True)
    password = CharField()
    email = CharField()
    registration_date = DateTimeField()
    last_active_date = DateTimeField()
    name = CharField(null=True)
    birthday = DateField(null=True)
    about = TextField(null=True)
    avatar = CharField(null=True)
    role = IntegerField(default=1)
