import datetime
import flask
import pytest
from src.model.user import User
from src.model.token import Token

def validate_tokens(json):
    assert 'access_token' in json

    access_token = Token.select().where(Token.is_refresh_token == False).get()
    assert json['access_token']['token'] == access_token.token
    assert json['access_token']['valid_until'] > datetime.datetime.now().timestamp() + 60 * 60 * 24 * 29
    assert json['access_token']['valid_until'] < datetime.datetime.now().timestamp() + 60 * 60 * 24 * 31
    assert User.get() == access_token.user

    refresh_token = Token.select().where(Token.is_refresh_token == True).get()
    assert json['refresh_token']['token'] == refresh_token.token
    assert json['refresh_token']['valid_until'] > datetime.datetime.now().timestamp() + 60 * 60 * 24 * 89
    assert json['refresh_token']['valid_until'] < datetime.datetime.now().timestamp() + 60 * 60 * 24 * 91
    assert User.get() == refresh_token.user

    assert refresh_token.token != access_token.token

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
        'password': 'some-pass',
        'name': 'name',
        'email': 'email',
    })
    assert User.select().count() == 1
    assert rv.status_code == 200
    assert rv.json['success'] == 1
    validate_tokens(rv.json)

def test_registration_not_all_data(client):
    rv = client.post('/users/register/', json={
        'username': 'test_user',
        'password': 'some-pass'
    })
    assert rv.status_code == 400
    assert rv.json['success'] == 0
    assert 'token' not in rv.json
    assert rv.json['error'] == '"Email" not in request, "Name" not in request'
    assert User.select().count() == 0
    assert Token.select().count() == 0

def test_registration_username_busy(client, user):
    rv = client.post('/users/register/', json={
        'username': 'test_user',
        'password': 'some-pass',
        'name': 'name',
        'email': 'email',
    })

    assert rv.status_code == 400
    assert rv.json['success'] == 0
    assert 'token' not in rv.json
    assert rv.json['error'] == 'User with this username already created'
    assert User.select().count() == 1
    assert Token.select().count() == 0

def test_registration_email_busy(client, user):
    rv = client.post('/users/register/', json={
        'username': 'test_user2',
        'password': 'some-pass',
        'name': 'name',
        'email': 'asd',
    })
    assert rv.status_code == 400
    assert rv.json['success'] == 0
    assert 'token' not in rv.json
    assert rv.json['error'] == 'User with this email already created'
    assert User.select().count() == 1
    assert Token.select().count() == 0

def test_registration_failure(client):
    rv = client.post('/users/register/', json={

    })
    assert rv.status_code == 400
    assert rv.json['success'] == 0
    assert 'token' not in rv.json
    assert User.select().count() == 0
    assert Token.select().count() == 0

def test_auth(client, user):
    rv = client.post('/users/login/', json={
        'username': 'test_user',
        'password': 'some-pass'
    })
    assert rv.status_code == 200
    assert rv.json['success'] == 1
    validate_tokens(rv.json)

def test_auth_wrong_password(client, user):
    rv = client.post('/users/login/', json={
        'username': 'test_user',
        'password': 'wrong-pass'
    })
    assert rv.status_code == 401
    assert rv.json['success'] == 0
    assert 'token' not in rv.json
    assert Token.select().count() == 0

def test_auth_wrong_user(client, user):
    rv = client.post('/users/login/', json={
        'username': 'test_user2',
        'password': 'some-pass'
    })
    assert rv.status_code == 401
    assert rv.json['success'] == 0
    assert 'token' not in rv.json
    assert Token.select().count() == 0

def test_auth_failure(client, user):
    rv = client.post('/users/login/', json={

    })
    assert rv.status_code == 400
    assert rv.json['success'] == 0
    assert 'token' not in rv.json
    assert Token.select().count() == 0