import datetime
import pytest
from src.model.models import User, Blog, BlogParticipiation, Content,\
    Token, BlogInvite


@pytest.fixture
def reader_token():
    user = User.create(
        login="reader",
        password="0x:993fadc17393cdfb06dfb7f5dd0d13de",
        email="asd",
        registration_date=datetime.datetime.now(),
        last_active_date=datetime.datetime.now())

    token = Token.generate_access_token(user)

    from src.model import db
    db.db_wrapper.database.close()

    return [user, token]


@pytest.fixture
def other_user_and_token():
    user = User.create(
        login="other_user",
        password="0x:993fadc17393cdfb06dfb7f5dd0d13de",
        email="asd",
        registration_date=datetime.datetime.now(),
        last_active_date=datetime.datetime.now())

    token = Token.generate_access_token(user)

    from src.model import db
    db.db_wrapper.database.close()

    return [user, token]


@pytest.fixture
def blog(user, reader_token):
    blog = Blog.create(
        title='test_blog', url='test_blog', creator=user,
        created_date=datetime.datetime.now(),
        updated_date=datetime.datetime.now())
    BlogParticipiation.create(blog=blog, user=user, role=1)

    writer = User.create(
        login="writer",
        password="0x:993fadc17393cdfb06dfb7f5dd0d13de",
        email="asd",
        registration_date=datetime.datetime.now(),
        last_active_date=datetime.datetime.now())
    BlogParticipiation.create(blog=blog, user=writer, role=2)

    BlogParticipiation.create(blog=blog, user=reader_token[0], role=3)

    from src.model import db
    db.db_wrapper.database.close()

    return blog


@pytest.fixture
def user_not_in_blog_with_token():
    user = User.create(
        login="user_not_in_blog",
        password="0x:993fadc17393cdfb06dfb7f5dd0d13de",
        email="asd",
        registration_date=datetime.datetime.now(),
        last_active_date=datetime.datetime.now(),
        name="name",
        birthday=datetime.date.today(),
        about="",
        avatar=None)

    token = Token.generate_access_token(user)

    from src.model import db
    db.db_wrapper.database.close()

    return [user, token]


@pytest.fixture
def blogs(user):
    for i in range(30):
        Blog.create(title='test_blog' + str(i), url='test_blog' + str(i), creator=user,
                    created_date=datetime.datetime.now(),
                    updated_date=datetime.datetime.now())

    from src.model import db
    db.db_wrapper.database.close()


def test_blogs(client, blog):
    rv = client.get('/blogs/')
    assert rv.json['success'] == 1
    assert len(rv.json['blogs']) == 1, 'We should have only one blog'
    assert rv.json['blogs'][0]['title'] == 'test_blog', 'With title test_blog'
    assert rv.json['blogs'][0]['readers'] == 3, 'Wrong count of readers'
    assert rv.json['meta']['page_count'] == 1, 'There should be one page'


def test_blogs_pagination(client, blogs):
    rv = client.get('/blogs/')
    assert len(rv.json['blogs']) == 20, \
        'We should have 20 blogs without pagination'
    assert rv.json['blogs'][0]['title'] == 'test_blog0', 'Wrong title'
    assert rv.json['meta']['page_count'] == 2, 'There should be two pages'

    rv = client.get('/blogs/?page=2')
    assert len(rv.json['blogs']) == 10,\
        'We should have 10 blogs on second page'
    assert rv.json['blogs'][0]['title'] == 'test_blog20', 'Wrong title'
    assert rv.json['meta']['page_count'] == 2, 'There should be two pages'

    rv = client.get('/blogs/?page=3')
    assert len(rv.json['blogs']) == 0,\
        'We should have 0 blogs on nonexistent page'


def test_empty_blogs(client):
    rv = client.get('/blogs/')
    assert len(rv.json['blogs']) == 0, 'We should have no blogs'
    assert rv.json['meta']['page_count'] == 0, 'There should be no pages'


def test_create_blog(client, user_token):
    rv = client.post(
        '/blogs/',
        headers={
            'Authorization': user_token[1].token
        })
    assert rv.json['success'] == 1
    assert 'blog' in rv.json, 'No blog in response'

    blog = Blog.get()
    assert blog.creator == user_token[0], 'Wrong creator'
    assert blog.id == rv.json['blog']['id']

    participiation = BlogParticipiation.get()
    assert participiation.blog.id == rv.json['blog']['id']
    assert participiation.user == user_token[0]
    assert participiation.role == 1, 'Not owner on creation'


def test_edit_blog(client, blog, user_token):
    rv = client.put(
        '/blogs/' + str(blog.url) + '/',
        json={
            'title': 'new title',
        },
        headers={
            'Authorization': user_token[1].token
        })
    assert rv.json['success'] == 1

    assert Blog.get().title == 'new title', 'Blog title not chaged'


def test_edit_blog_wrong_user(client, blog, user_not_in_blog_with_token):
    rv = client.put(
        '/blogs/' + str(blog.url) + '/',
        json={
            'title': 'new title',
        },
        headers={
            'Authorization': user_not_in_blog_with_token[1].token
        })
    assert rv.json['success'] == 0
    assert rv.json['error'] == 'You doesn\'t have rights to do this action'

    assert Blog.get().title == blog.title, 'Blog title changed'
    assert Blog.get().title != 'new title'


def test_edit_blog_reader(client, blog, reader_token):
    rv = client.put(
        '/blogs/' + str(blog.url) + '/',
        json={
            'title': 'new title',
        },
        headers={
            'Authorization': reader_token[1].token
        })
    assert rv.json['success'] == 0
    assert rv.json['error'] == 'You doesn\'t have rights to do this action'

    assert Blog.get().title == blog.title, 'Blog title changed'
    assert Blog.get().title != 'new title'


def test_delete_blog(client, blog, user_token):
    rv = client.delete(
        '/blogs/' + str(blog.url) + '/',
        headers={
            'Authorization': user_token[1].token
        })
    assert rv.json['success'] == 1

    assert Blog.select().count() == 0, 'Blog not deleted'


def test_delete_blog_wrong_user(client, blog, user_not_in_blog_with_token):
    rv = client.delete(
        '/blogs/' + str(blog.url) + '/',
        headers={
            'Authorization': user_not_in_blog_with_token[1].token
        })
    assert rv.json['success'] == 0
    assert rv.json['error'] == 'You doesn\'t have rights to do this action'

    assert Blog.select().count() == 1, 'Blog was deleted'


def test_delete_blog_reader(client, blog, reader_token):
    rv = client.delete(
        '/blogs/' + str(blog.url) + '/',
        headers={
            'Authorization': reader_token[1].token
        })
    assert rv.json['success'] == 0
    assert rv.json['error'] == 'You doesn\'t have rights to do this action'

    assert Blog.select().count() == 1, 'Blog was deleted'


def test_blog(client, blog):
    rv = client.get('/blogs/' + str(blog.url) + '/')
    assert rv.json['success'] == 1
    assert rv.json['blog']['title'] == blog.title, 'Wrong blog title'
    assert rv.json['blog']['readers'] == 3, 'Wrong count of readers'


def test_blog_readers(client, blog):
    rv = client.get('/blogs/' + str(blog.url) + '/readers/')
    assert rv.json['success'] == 1
    assert len(rv.json['readers']) == 3, 'Wrong count of readers'
    assert 'name' in rv.json['readers'][0], 'Readers schema'

    user1 = rv.json['readers'][0]
    user2 = rv.json['readers'][1]
    assert user1['name'] != user2['name']

    assert rv.json['meta']['page_count'] == 1, 'There should be one page'


def test_blog_invite(client, blog, user_token, user_not_in_blog_with_token):
    body = {
        'user': user_not_in_blog_with_token[0].id,
        'role': 'writer'
    }

    rv = client.post(
        '/blogs/' + str(blog.url) + '/invite/',
        headers={
            'Authorization': user_token[1].token
        },
        json=body)

    assert rv.json['success'] == 1
    assert 'invite' in rv.json
    assert BlogInvite.select().count() == 1, 'There should be one invite'

    invite = BlogInvite.get()
    assert invite.blog.id == blog.id
    assert invite.user_from.id == user_token[0].id
    assert invite.user_to.id == user_not_in_blog_with_token[0].id
    assert invite.role == 2
    assert not invite.is_accepted

    query = BlogParticipiation\
        .select()\
        .where(
            (BlogParticipiation.user == user_not_in_blog_with_token[0]) &
            (BlogParticipiation.blog == blog))

    assert query.count() == 0, 'User should not be added to blog'

    from src.model import db
    db.db_wrapper.database.close()

    rv = client.post(
        '/blogs/' + str(blog.url) + '/invite/',
        headers={
            'Authorization': user_not_in_blog_with_token[1].token
        },
        json={
            'invite': rv.json['invite']
        })
    assert rv.json['success'] == 1
    assert BlogInvite.select().count() == 1, 'There should be one invite'

    invite = BlogInvite.get()
    assert invite.blog.id == blog.id
    assert invite.user_from.id == user_token[0].id
    assert invite.user_to.id == user_not_in_blog_with_token[0].id
    assert invite.role == 2
    assert invite.is_accepted

    assert query.count() == 1, 'User should be added to blog'

    participiation = query.get()
    assert participiation.role == 2


def test_blog_invite_cant_accept_other_user(
        client, blog, user_token, user_not_in_blog_with_token,
        other_user_and_token):

    body = {
        'user': user_not_in_blog_with_token[0].id,
        'role': 'writer'
    }

    rv = client.post(
        '/blogs/' + str(blog.url) + '/invite/',
        headers={
            'Authorization': user_token[1].token
        },
        json=body)
    assert rv.json['success'] == 1
    assert 'invite' in rv.json
    assert BlogInvite.select().count() == 1, 'There should be one invite'

    invite = BlogInvite.get()
    assert invite.blog.id == blog.id
    assert invite.user_from.id == user_token[0].id
    assert invite.user_to.id == user_not_in_blog_with_token[0].id
    assert invite.role == 2
    assert not invite.is_accepted

    query = BlogParticipiation\
        .select()\
        .where(
            (BlogParticipiation.user == user_not_in_blog_with_token[0]) &
            (BlogParticipiation.blog == blog))

    assert query.count() == 0, 'User should not be added to blog'

    from src.model import db
    db.db_wrapper.database.close()

    rv = client.post(
        '/blogs/' + str(blog.url) + '/invite/',
        headers={
            'Authorization': other_user_and_token[1].token
        },
        json={
            'invite': rv.json['invite']
        })
    assert rv.json['success'] == 0
    assert rv.json['error'] == 'You can\'t accept this invite'
    assert BlogInvite.select().count() == 1, 'There should be one invite'

    invite = BlogInvite.get()
    assert invite.blog.id == blog.id
    assert invite.user_from.id == user_token[0].id
    assert invite.user_to.id == user_not_in_blog_with_token[0].id
    assert invite.role == 2
    assert not invite.is_accepted

    query = BlogParticipiation\
        .select()\
        .where(
            (BlogParticipiation.user == user_not_in_blog_with_token[0]) &
            (BlogParticipiation.blog == blog))
    assert query.count() == 0, 'User should not be added to blog'

    query = BlogParticipiation\
        .select()\
        .where(
            (BlogParticipiation.user == other_user_and_token[0]) &
            (BlogParticipiation.blog == blog))
    assert query.count() == 0, 'Other user should not be added to blog'


def test_blog_invite_incorrect(client, blog, user_token,
                               user_not_in_blog_with_token):

    body = {
        'user': user_not_in_blog_with_token[0].id,
        'role': 'writer'
    }
    rv = client.post('/blogs/' + str(blog.url) + '/invite/', json=body)
    assert rv.json['success'] == 0
    assert rv.json['error'] == 'You should be authorized to use this endpoint'
    assert BlogInvite.select().count() == 0, 'There should be no invites'

    from src.model import db
    db.db_wrapper.database.close()

    rv = client.post(
        '/blogs/' + str(blog.url) + '/invite/',
        headers={
            'Authorization': user_not_in_blog_with_token[1].token
        },
        json=body)
    assert rv.json['success'] == 0
    assert rv.json['error'] == 'You are not participiate in this blog'
    assert BlogInvite.select().count() == 0, 'There should be no invites'


def test_blog_invite_from_reader(client, blog, reader_token,
                                 user_not_in_blog_with_token):

    body = {
        'user': user_not_in_blog_with_token[0].id,
        'role': 'writer'
    }

    rv = client.post(
        '/blogs/' + str(blog.url) + '/invite/',
        headers={
            'Authorization': reader_token[1].token
        },
        json=body)
    assert rv.json['success'] == 0
    assert rv.json['error'] == 'You doesn\'t have rights to do this action'
    assert BlogInvite.select().count() == 0, 'There should be no invites'

    body = {
        'user': user_not_in_blog_with_token[0].id,
        'role': 'reader'
    }

    from src.model import db
    db.db_wrapper.database.close()

    rv = client.post(
        '/blogs/' + str(blog.url) + '/invite/',
        headers={
            'Authorization': reader_token[1].token
        },
        json=body)
    assert rv.json['success'] == 1
    assert BlogInvite.select().count() == 1, 'There should be one invite'

    invite = BlogInvite.get()
    assert invite.blog.id == blog.id
    assert invite.user_from.id == reader_token[0].id
    assert invite.user_to.id == user_not_in_blog_with_token[0].id
    assert invite.role == 3
