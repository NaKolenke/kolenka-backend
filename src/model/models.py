import datetime
import secrets
from peewee import *
from src.model import db


class Content(db.db_wrapper.Model):
    user = IntegerField()
    path = CharField()


class User(db.db_wrapper.Model):
    login = CharField(unique=True)
    password = CharField()
    email = CharField()
    registration_date = DateTimeField()
    last_active_date = DateTimeField()
    name = CharField(null=True)
    birthday = DateField(null=True)
    about = TextField(null=True)
    role = IntegerField(default=1)

    avatar = ForeignKeyField(model=Content, backref='avatar', null=True)


class Token(db.db_wrapper.Model):
    user = ForeignKeyField(model=User, backref='token')
    token = CharField()
    valid_until = DateTimeField()
    is_refresh_token = BooleanField()

    @classmethod
    def generate_access_token(cls, user):
        return cls.create(user=user, token=secrets.token_hex(), is_refresh_token=False, valid_until=datetime.datetime.now() + datetime.timedelta(days=30))

    @classmethod
    def generate_refresh_token(cls, user):
        return cls.create(user=user, token=secrets.token_hex(), is_refresh_token=True, valid_until=datetime.datetime.now() + datetime.timedelta(days=90))
