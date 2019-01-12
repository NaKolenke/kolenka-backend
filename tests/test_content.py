import os
import datetime
import flask
import pytest
from src.model.models import User, Token

@pytest.fixture
def user_token():
    user = User.create(login="test_user", password="0x:993fadc17393cdfb06dfb7f5dd0d13de", email="asd", registration_date=datetime.datetime.now(
    ), last_active_date=datetime.datetime.now(), name="name", birthday=datetime.date.today(), about="", avatar=None)

    token = Token.generate_access_token(user)

    from src.model import db
    db.db_wrapper.database.close()

    return [user, token]

def test_content(client, user_token):
    if os.path.isfile('uploads/test_user1.png'):
        os.unlink('uploads/test_user1.png')

    rv = client.post('/content/',
                     data=dict(
                         file=(open('testing-data/1.png', 'rb'), 'testing-data/1.png'),
                     ),
                     headers={
                         'authorization': user_token[1].token
                     })
    assert rv.status_code == 200
    assert rv.json['success'] == 1
    assert 'id' in rv.json['file'], 'There should be id field'

    assert os.path.getsize('testing-data/1.png') == os.path.getsize('uploads/test_user1.png'), 'There is a problem with image uploading'

    rv = client.get('/content/' + str(rv.json['file']['id']) + '/')
    assert len(rv.data) == os.path.getsize('testing-data/1.png'), 'Uploaded image has wrong size'
