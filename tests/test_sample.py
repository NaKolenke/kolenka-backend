import os
import tempfile

import pytest

from src import main


@pytest.fixture
def client():
    # db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
    main.app.config['TESTING'] = True
    client = main.app.test_client()

    # with flaskr.app.app_context():
    # flaskr.init_db()

    yield client

    # os.close(db_fd)
    # os.unlink(flaskr.app.config['DATABASE'])


def test_sample(client):
    """Start with a blank database."""

    rv = client.get('/')
    assert b'Hello World!' in rv.data
