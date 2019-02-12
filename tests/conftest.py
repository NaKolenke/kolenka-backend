import os
import pytest
import datetime
from src.model.models import User, Token, Blog, BlogParticipiation, Post,\
    Comment


@pytest.fixture(scope="function")
def client():
    os.environ['KOLENKA_CONFIG'] = 'config/test.cfg'

    import src
    app = src.create_app()
    app.testing = True
    client = app.test_client()

    yield client

    from src.model import db
    db.db_wrapper.database.close()
    os.unlink(app.config['DATABASE_FOR_REMOVE'])


@pytest.fixture
def user():
    user = User.create(
        login="test_user",
        password="0x:993fadc17393cdfb06dfb7f5dd0d13de",
        email="asd",
        registration_date=datetime.datetime.now(),
        last_active_date=datetime.datetime.now(),
        name="name",
        birthday=datetime.date.today(),
        about="",
        avatar=None)

    from src.model import db
    db.db_wrapper.database.close()

    return user


@pytest.fixture
def user_token(user):
    token = Token.generate_access_token(user)

    from src.model import db
    db.db_wrapper.database.close()

    return [user, token]


@pytest.fixture
def admin_token():
    user = User.create(
        login="admin_with_token",
        password="0x:993fadc17393cdfb06dfb7f5dd0d13de",
        email="asd",
        registration_date=datetime.datetime.now(),
        last_active_date=datetime.datetime.now(),
        name="name",
        birthday=datetime.date.today(),
        about="",
        avatar=None,
        is_admin=True)

    token = Token.generate_access_token(user)

    from src.model import db
    db.db_wrapper.database.close()

    return [user, token]


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
def post(user, blog):
    post = Post.create(
        blog=blog,
        creator=user,
        created_date=datetime.datetime.now(),
        updated_date=datetime.datetime.now(),
        title="Some post title",
        text="Some text",
        cut_text="Cut text",
        rating=0,
        is_draft=False,
        is_on_main=True,
        url="url-for-post")

    from src.model import db
    db.db_wrapper.database.close()

    return post


@pytest.fixture
def comment(user, post):
    comment = Comment.create(
        post=post,
        creator=user,
        created_date=datetime.datetime.now(),
        updated_date=datetime.datetime.now(),
        text="Some text")

    from src.model import db
    db.db_wrapper.database.close()

    return comment
