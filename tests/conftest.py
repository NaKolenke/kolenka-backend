import os

import pytest

@pytest.fixture(scope="function")
def client():
    os.environ['KOLENKA_CONFIG'] = 'config/test.cfg'

    import src
    app = src.create_app()
    app.testing = True
    client = app.test_client()

    yield client

    from src.model import db
    db.db_wrapper.database.close()
    os.unlink(app.config['DATABASE_FOR_REMOVE'])
