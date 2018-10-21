from peewee import *
from src.model.db import get_database

class BaseModel(Model):
    class Meta:
        database = get_database()
