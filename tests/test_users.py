import datetime
import pytest
from src.model.models import (
    User,
    Token,
    Content,
    Blog,
    BlogParticipiation,
    AchievementUser,
    Achievement,
)


def validate_tokens(json):
    assert "access_token" in json
    assert "refresh_token" in json

    access_token = Token.select().where(Token.token_type == "access").get()
    assert json["access_token"]["token"] == access_token.token
    assert (
        json["access_token"]["valid_until"]
        > datetime.datetime.now().timestamp() + 60 * 60 * 24 * 29
    )

    assert (
        json["access_token"]["valid_until"]
        < datetime.datetime.now().timestamp() + 60 * 60 * 24 * 31
    )

    assert User.get() == access_token.user

    refresh_token = Token.select().where(Token.token_type == "refresh").get()
    assert json["refresh_token"]["token"] == refresh_token.token
    assert (
        json["refresh_token"]["valid_until"]
        > datetime.datetime.now().timestamp() + 60 * 60 * 24 * 89
    )

    assert (
        json["refresh_token"]["valid_until"]
        < datetime.datetime.now().timestamp() + 60 * 60 * 24 * 91
    )

    assert User.get() == refresh_token.user

    assert refresh_token.token != access_token.token


@pytest.fixture
def avatar():
    avatar = Content.create(user=1, path="/some/path", mime="image/jpeg", size=1)

    from src.model import db

    db.db_wrapper.database.close()

    return avatar


@pytest.fixture
def blog(user):
    blog = Blog.create(
        title="test_blog",
        url="test_blog",
        creator=user,
        created_date=datetime.datetime.now(),
        updated_date=datetime.datetime.now(),
    )
    BlogParticipiation.create(blog=blog, user=user, role=1)

    from src.model import db

    db.db_wrapper.database.close()

    return blog


@pytest.fixture
def achievement(user):
    achievement = Achievement.create(title="test achievement", image=None)
    AchievementUser.create(achievement=achievement, user=user, comment="some comment")

    from src.model import db

    db.db_wrapper.database.close()

    return achievement


@pytest.fixture
def users():
    for i in range(30):
        User.create(
            username="test_user" + str(i),
            password="0x:993fadc17393cdfb06dfb7f5dd0d13de",
            email="asd" + str(i),
            registration_date=datetime.datetime.now(),
            last_active_date=datetime.datetime.now(),
            name="name",
            birthday=datetime.date.today(),
            about="",
            avatar=None,
        )

    from src.model import db

    db.db_wrapper.database.close()


def test_users(client, user):
    rv = client.get("/users/")
    assert len(rv.json["users"]) == 1, "We should have only one user"
    assert rv.json["users"][0]["username"] == "test_user", "With name test_user"
    assert rv.json["meta"]["page_count"] == 1, "There should be one page"

    assert "achievements" not in rv.json["users"][0]


def test_users_pagination(client, users):
    rv = client.get("/users/")
    assert len(rv.json["users"]) == 20, "We should have 20 users without pagination"
    assert rv.json["users"][0]["username"] == "test_user29", "With name test_user29"
    assert rv.json["meta"]["page_count"] == 2, "There should be two pages"

    rv = client.get("/users/?page=2")
    assert len(rv.json["users"]) == 10, "We should have 10 users on second page"
    assert rv.json["users"][0]["username"] == "test_user9", "Wrong username"
    assert rv.json["meta"]["page_count"] == 2, "There should be two pages"

    rv = client.get("/users/?page=3")
    assert len(rv.json["users"]) == 0, "We should have 0 users on nonexistent page"


def test_empty_users(client):
    rv = client.get("/users/")
    assert len(rv.json["users"]) == 0, "We should have no users"
    assert rv.json["meta"]["page_count"] == 0, "There should be no pages"


def test_user(client, user, achievement):
    rv = client.get("/users/" + str(user.username) + "/")
    assert rv.json["success"] == 1
    assert rv.json["user"]["username"] == "test_user", "With name test_user"

    assert "achievements" in rv.json["user"]
    assert rv.json["user"]["achievements"][0]["title"] == achievement.title
    assert rv.json["user"]["achievements"][0]["comment"] == "some comment"


def test_wrong_user(client, user):
    rv = client.get("/users/" + user.username + str(1) + "/")
    assert rv.json["success"] == 0
    assert "user" not in rv.json
    assert rv.json["error"]["code"] == 4


def test_user_edit_no_auth(client, user_token):
    rv = client.post("/users/self/", json={"name": "other name"})
    assert rv.json["success"] == 0
    assert rv.json["error"]["code"] == 1


def test_user_edit(client, user_token):
    rv = client.post(
        "/users/self/",
        json={"name": "other name"},
        headers={"Authorization": user_token[1].token},
    )
    assert rv.json["success"] == 1
    assert rv.json["user"]["name"] == "other name", "Name not changed"
    assert rv.json["user"]["about"] == ""

    rv = client.post(
        "/users/self/",
        json={"about": "about text"},
        headers={"Authorization": user_token[1].token},
    )
    assert rv.json["success"] == 1
    assert rv.json["user"]["name"] == "other name", "Name was changed"
    assert rv.json["user"]["about"] == "about text", "About not changed"


def test_user_edit_avatar(client, user_token, avatar):
    rv = client.post(
        "/users/self/",
        json={"avatar": avatar.id},
        headers={"Authorization": user_token[1].token},
    )
    assert rv.json["success"] == 1
    assert rv.json["user"]["avatar"]["id"] == avatar.id, "Avatar not changed"


def test_user_get_self(client, user_token):
    rv = client.get("/users/self/", headers={"Authorization": user_token[1].token})
    assert rv.json["success"] == 1
    assert rv.json["user"]["name"] == user_token[0].name
    assert "email" in rv.json["user"]


def test_registration(client):
    rv = client.post(
        "/users/register/",
        json={
            "username": "test_user",
            "password": "some-pass",
            "name": "name",
            "email": "email",
        },
    )
    assert User.select().count() == 1
    assert rv.status_code == 200
    assert rv.json["success"] == 1
    validate_tokens(rv.json)


def test_registration_not_all_data(client):
    rv = client.post(
        "/users/register/", json={"username": "test_user", "password": "some-pass"}
    )
    assert rv.status_code == 400
    assert rv.json["success"] == 0
    assert "token" not in rv.json
    assert rv.json["error"]["code"] == 5
    assert User.select().count() == 0
    assert Token.select().count() == 0


def test_registration_username_busy(client, user):
    rv = client.post(
        "/users/register/",
        json={
            "username": "test_user",
            "password": "some-pass",
            "name": "name",
            "email": "email",
        },
    )

    assert rv.status_code == 400
    assert rv.json["success"] == 0
    assert "token" not in rv.json
    assert rv.json["error"]["code"] == 13
    assert User.select().count() == 1
    assert Token.select().count() == 0


def test_registration_email_busy(client, user):
    rv = client.post(
        "/users/register/",
        json={
            "username": "test_user2",
            "password": "some-pass",
            "name": "name",
            "email": "asd",
        },
    )
    assert rv.status_code == 400
    assert rv.json["success"] == 0
    assert "token" not in rv.json
    assert rv.json["error"]["code"] == 12
    assert User.select().count() == 1
    assert Token.select().count() == 0


def test_registration_failure(client):
    rv = client.post("/users/register/", json={})
    assert rv.status_code == 400
    assert rv.json["success"] == 0
    assert "token" not in rv.json
    assert User.select().count() == 0
    assert Token.select().count() == 0


def test_auth(client, user):
    rv = client.post(
        "/users/login/", json={"username": "test_user", "password": "some-pass"}
    )
    assert rv.status_code == 200
    assert rv.json["success"] == 1
    validate_tokens(rv.json)


def test_auth_wrong_password(client, user):
    rv = client.post(
        "/users/login/", json={"username": "test_user", "password": "wrong-pass"}
    )
    assert rv.status_code == 401
    assert rv.json["success"] == 0
    assert "token" not in rv.json
    assert Token.select().count() == 0


def test_auth_wrong_user(client, user):
    rv = client.post(
        "/users/login/", json={"username": "test_user2", "password": "some-pass"}
    )
    assert rv.status_code == 401
    assert rv.json["success"] == 0
    assert "token" not in rv.json
    assert Token.select().count() == 0


def test_auth_failure(client, user):
    rv = client.post("/users/login/", json={})
    assert rv.status_code == 400
    assert rv.json["success"] == 0
    assert "token" not in rv.json
    assert Token.select().count() == 0


def test_user_blogs(client, user, blog):
    rv = client.get("/users/" + str(user.username) + "/blogs/")
    assert rv.json["success"] == 1
    assert len(rv.json["blogs"]) == 1, "Wrong count of blogs"
    assert "title" in rv.json["blogs"][0], "Blogs schema"

    assert rv.json["meta"]["page_count"] == 1, "There should be one page"
