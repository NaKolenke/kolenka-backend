import os
import pytest
import datetime
from src.model.models import User, Token


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


@pytest.fixture
def user():
    user = User.create(
        login="test_user",
        password="0x:993fadc17393cdfb06dfb7f5dd0d13de",
        email="asd",
        registration_date=datetime.datetime.now(),
        last_active_date=datetime.datetime.now(),
        name="name",
        birthday=datetime.date.today(),
        about="",
        avatar=None)

    from src.model import db
    db.db_wrapper.database.close()

    return user


@pytest.fixture
def user_token(user):
    token = Token.generate_access_token(user)

    from src.model import db
    db.db_wrapper.database.close()

    return [user, token]


@pytest.fixture
def admin_token():
    user = User.create(
        login="admin_with_token",
        password="0x:993fadc17393cdfb06dfb7f5dd0d13de",
        email="asd",
        registration_date=datetime.datetime.now(),
        last_active_date=datetime.datetime.now(),
        name="name",
        birthday=datetime.date.today(),
        about="",
        avatar=None,
        role=2)

    token = Token.generate_access_token(user)

    from src.model import db
    db.db_wrapper.database.close()

    return [user, token]
