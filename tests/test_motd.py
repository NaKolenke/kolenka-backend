def test_motd(client):
    rv = client.get('/')
    assert b'You are at the main page of kolenka api' in rv.data
