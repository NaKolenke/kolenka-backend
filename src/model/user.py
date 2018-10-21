from peewee import *
from src.model.model import BaseModel

class User(BaseModel):
    name = CharField()
