import os
import platform
import datetime


def test_content(client, user_token):
    if platform.system() == 'Windows':
        # skip, because content needs specific native library
        return
    today = datetime.date.today()
    filename = str(user_token[0].id) + '/'\
        + str(today.year) + '/'\
        + str(today.month) + '/' + '06316e26031f7c69c9cb7de53541e8e0.png'
    if os.path.isfile('uploads/' + filename):
        os.unlink('uploads/' + filename)

    rv = client.post('/content/',
                     data=dict(
                         file=(
                             open('testing-data/1.png', 'rb'),
                             'testing-data/1.png'),
                     ),
                     headers={
                         'authorization': user_token[1].token
                     })
    assert rv.status_code == 200
    assert rv.json['success'] == 1
    assert 'id' in rv.json['file'], 'There should be id field'

    assert os.path.getsize('testing-data/1.png') == \
        os.path.getsize('uploads/' + filename), \
        'There is a problem with image uploading'

    rv = client.get('/content/' + str(rv.json['file']['id']) + '/')
    assert len(rv.data) == os.path.getsize('testing-data/1.png'), \
        'Uploaded image has wrong size'
