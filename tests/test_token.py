import datetime
import pytest
from src.model.models import User, Token

def validate_tokens(json):
    assert 'access_token' in json
    assert 'refresh_token' in json

    access_token = Token.select().where((Token.token_type == 'access') & (Token.token == json['access_token']['token'])).get()
    assert json['access_token']['valid_until'] > datetime.datetime.now().timestamp() + 60 * 60 * 24 * 29
    assert json['access_token']['valid_until'] < datetime.datetime.now().timestamp() + 60 * 60 * 24 * 31
    assert User.get() == access_token.user

    refresh_token = Token.select().where((Token.token_type == 'refresh') & (Token.token == json['refresh_token']['token'])).get()
    assert json['refresh_token']['valid_until'] > datetime.datetime.now().timestamp() + 60 * 60 * 24 * 89
    assert json['refresh_token']['valid_until'] < datetime.datetime.now().timestamp() + 60 * 60 * 24 * 91
    assert User.get() == refresh_token.user

    assert refresh_token.token != access_token.token

@pytest.fixture
def tokens():
    user = User.create(username="test_user", password="0x:993fadc17393cdfb06dfb7f5dd0d13de", email="asd", registration_date=datetime.datetime.now(), last_active_date=datetime.datetime.now(), name="name", birthday=datetime.date.today(), about="", avatar=None)

    a = Token.generate_access_token(user)
    r = Token.generate_refresh_token(user)

    from src.model import db
    db.db_wrapper.database.close()

    return {
        'access_token': a,
        'refresh_token': r
    }

def test_token_valid(client, tokens):
    rv = client.post('/token/validate/', json={
        'token': tokens['access_token'].token
    })
    assert rv.status_code == 200
    assert rv.json['success'] == 1

def test_token_invalid(client, tokens):
    rv = client.post('/token/validate/', json={
        'token': '0'
    })
    assert rv.status_code == 400
    assert rv.json['success'] == 0
    assert rv.json['error']['code'] == 10

def test_token_outdated(client, tokens):
    tokens['access_token'].valid_until=datetime.datetime.now()
    tokens['access_token'].save()

    from src.model import db
    db.db_wrapper.database.close()

    rv = client.post('/token/validate/', json={
        'token': tokens['access_token'].token
    })
    assert rv.status_code == 400
    assert rv.json['success'] == 0
    assert rv.json['error']['code'] == 11

def test_refresh_token(client, tokens):
    rv = client.post('/token/refresh/', json={
        'token': tokens['refresh_token'].token
    })
    assert rv.status_code == 200
    assert rv.json['success'] == 1
    validate_tokens(rv.json)

def test_refresh_token_invalid(client, tokens):
    rv = client.post('/token/refresh/', json={
        'token': '0'
    })
    assert rv.status_code == 400
    assert rv.json['success'] == 0
    assert rv.json['error']['code'] == 10
    assert 'access_token' not in rv.json

def test_refresh_token_outdated(client, tokens):
    tokens['refresh_token'].valid_until=datetime.datetime.now()
    tokens['refresh_token'].save()
    from src.model import db
    db.db_wrapper.database.close()

    rv = client.post('/token/refresh/', json={
        'token': tokens['refresh_token'].token
    })
    assert rv.status_code == 400
    assert rv.json['success'] == 0
    assert rv.json['error']['code'] == 11
    assert 'access_token' not in rv.json

def test_self(client, tokens):
    headers = {
        'Authorization': tokens['access_token'].token
    }
    rv = client.get('/users/self/', headers=headers)
    assert rv.status_code == 200
    assert 'user' in rv.json
    assert rv.json['user']['username'] == 'test_user'

def test_self_not_authorized(client, tokens):
    rv = client.get('/users/self/')
    assert rv.status_code == 401
    assert rv.json['success'] == 0
    assert rv.json['error']['code'] == 1
    assert 'user' not in rv.json
