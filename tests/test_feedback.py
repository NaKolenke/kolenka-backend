import datetime
import pytest
from src.model.models import User, Feedback

@pytest.fixture
def feedback():
    user = User.create(login="feedback_user", password="0x:993fadc17393cdfb06dfb7f5dd0d13de", email="asd", registration_date=datetime.datetime.now(
    ), last_active_date=datetime.datetime.now(), name="name", birthday=datetime.date.today(), about="", avatar=None)

    feedback = Feedback.create(text='some text', user=user)

    from src.model import db
    db.db_wrapper.database.close()

def test_leave_feedback(client, user_token):
    rv = client.post('/feedback/',
                     json={
                         'text': 'some text'
                     },
                     headers={
                         'authorization': user_token[1].token
                     })
    assert rv.status_code == 200
    assert rv.json['success'] == 1
    assert Feedback.select().count() == 1

def test_leave_feedback_no_text(client, user_token):
    rv = client.post('/feedback/',
                     json={
                     },
                     headers={
                         'authorization': user_token[1].token
                     })
    assert rv.status_code == 200
    assert rv.json['success'] == 0
    assert rv.json['error'] == 'No text provided'
    assert Feedback.select().count() == 0


def test_leave_feedback_no_auth(client, user_token):
    rv = client.post('/feedback/',
                     json={
                         'text': 'some text'
                     })
    assert rv.status_code == 401
    assert rv.json['success'] == 0
    assert rv.json['error'] == 'You should be authorized to use this endpoint'
    assert Feedback.select().count() == 0


def test_get_feedback_not_admin(client, user_token, feedback):
    rv = client.get('/feedback/',
                     headers={
                         'authorization': user_token[1].token
                     })
    assert rv.status_code == 200
    assert rv.json['success'] == 0
    assert rv.json['error'] == 'Current user doesn\'t have rights to this action'
    assert 'feedback' not in rv.json

    rv = client.get('/feedback/1/',
                     headers={
                         'authorization': user_token[1].token
                     })
    assert rv.status_code == 200
    assert rv.json['success'] == 0
    assert rv.json['error'] == 'Current user doesn\'t have rights to this action'

def test_get_feedback(client, admin_token, feedback):
    rv = client.get('/feedback/',
                     headers={
                         'authorization': admin_token[1].token
                     })
    assert rv.status_code == 200
    assert rv.json['success'] == 1
    assert len(rv.json['feedback']) == 1
    assert rv.json['feedback'][0]['text'] == 'some text'
    assert rv.json['feedback'][0]['is_resolved'] == False

    rv = client.get('/feedback/1/',
                     headers={
                         'authorization': admin_token[1].token
                     })
    assert rv.status_code == 200
    assert rv.json['success'] == 1

    rv = client.get('/feedback/',
                     headers={
                         'authorization': admin_token[1].token
                     })
    assert rv.status_code == 200
    assert rv.json['success'] == 1
    assert len(rv.json['feedback']) == 1
    assert rv.json['feedback'][0]['text'] == 'some text'
    assert rv.json['feedback'][0]['is_resolved'] == True
