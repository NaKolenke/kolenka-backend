import datetime
import pytest
from src.model.user import User

@pytest.fixture
def user():
    User.create(login="Test", password="12", email="asd", registration_date=datetime.datetime.now(), last_active_date=datetime.datetime.now(), name="name", birthday=datetime.date.today(), about="", avatar="")

    from src.model import db
    db.db_wrapper.database.close()

def test_users(client, user):
    rv = client.get('/users/')
    assert len(rv.json) == 1, 'We should have only one user'
    assert rv.json[0]['login'] == 'Test', 'With name Test'

def test_users(client):
    rv = client.get('/users/')
    assert len(rv.json) == 0, 'We should have no users'
    assert str(rv.json) == '[]'
