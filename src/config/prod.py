from src.config.default import Config
class Prod(Config):
    DEBUG = False
    DATABASE_URI = 'sqlite:///:memory:'
