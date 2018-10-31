import datetime
import flask
import pytest
from src.model.user import User

@pytest.fixture
def user():
    User.create(login="test_user", password="0x:993fadc17393cdfb06dfb7f5dd0d13de", email="asd", registration_date=datetime.datetime.now(), last_active_date=datetime.datetime.now(), name="name", birthday=datetime.date.today(), about="", avatar="")

    from src.model import db
    db.db_wrapper.database.close()

def test_users(client, user):
    rv = client.get('/users/')
    assert len(rv.json) == 1, 'We should have only one user'
    assert rv.json[0]['login'] == 'test_user', 'With name test_user'

def test_empty_users(client):
    rv = client.get('/users/')
    assert len(rv.json) == 0, 'We should have no users'
    assert str(rv.json) == '[]'

def test_registration(client):
    rv = client.post('/users/register/', json={
        'username': 'test_user',
        'password': 'some-pass'
    })
    assert rv.status_code == 200
    assert rv.json['success'] == 1
    assert 'token' in rv.json

def test_registration_failure(client):
    rv = client.post('/users/register/', json={

    })
    assert rv.status_code == 400
    assert rv.json['success'] == 0
    assert 'token' not in rv.json

def test_auth(client, user):
    rv = client.post('/users/login/', json={
        'username': 'test_user',
        'password': 'some-pass'
    })
    assert rv.status_code == 200
    assert rv.json['success'] == 1
    assert 'token' in rv.json

def test_auth_wrong_password(client, user):
    rv = client.post('/users/login/', json={
        'username': 'test_user',
        'password': 'wrong-pass'
    })
    assert rv.status_code == 401
    assert rv.json['success'] == 0
    assert 'token' not in rv.json

def test_auth_wrong_user(client, user):
    rv = client.post('/users/login/', json={
        'username': 'test_user2',
        'password': 'some-pass'
    })
    assert rv.status_code == 401
    assert rv.json['success'] == 0
    assert 'token' not in rv.json

def test_auth_failure(client, user):
    rv = client.post('/users/login/', json={

    })
    assert rv.status_code == 400
    assert rv.json['success'] == 0
    assert 'token' not in rv.json