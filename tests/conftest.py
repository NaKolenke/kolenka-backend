import os

import pytest

from src.config.test import TestConfig

@pytest.fixture(scope="function")
def client():
    os.environ['KOLENKA_CONFIG'] = 'src.config.test.TestConfig'

    import src
    app = src.create_app()
    app.testing = True
    client = app.test_client()

    yield client

    from src.model import db
    db.db_wrapper.database.close()
    os.unlink(TestConfig.DATABASE_FOR_REMOVE)
