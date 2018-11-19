import datetime
import secrets
from peewee import *
from src.model import db
from src.model.user import User

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
