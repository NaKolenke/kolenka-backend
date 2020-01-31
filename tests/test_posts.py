import datetime
import pytest
from src.model.models import User, Token, Post, Comment


@pytest.fixture
def user_not_in_blog_with_token():
    user = User.create(
        username="user_not_in_blog",
        password="0x:993fadc17393cdfb06dfb7f5dd0d13de",
        email="asd",
        registration_date=datetime.datetime.now(),
        last_active_date=datetime.datetime.now(),
        name="name",
        birthday=datetime.date.today(),
        about="",
        avatar=None,
    )

    token = Token.generate_access_token(user)

    from src.model import db

    db.db_wrapper.database.close()

    return [user, token]


@pytest.fixture
def post_not_on_main(user, blog):
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
        is_on_main=False,
        url="url-for-post",
    )

    from src.model import db

    db.db_wrapper.database.close()

    return post


@pytest.fixture
def draft_post(user, blog):
    post = Post.create(
        blog=blog,
        creator=user,
        created_date=datetime.datetime.now(),
        updated_date=datetime.datetime.now(),
        title="Some post title",
        text="Some text",
        cut_text="Cut text",
        rating=0,
        is_draft=True,
        is_on_main=False,
        url="url-for-draft-post",
    )

    from src.model import db

    db.db_wrapper.database.close()

    return post


def test_posts(client, post):
    rv = client.get("/posts/")
    assert rv.json["success"] == 1
    assert len(rv.json["posts"]) == 1, "We should have only one post"
    assert rv.json["posts"][0]["title"] == post.title, "Wrong title"
    assert rv.json["meta"]["page_count"] == 1, "There should be one page"


def test_posts_no_post(client):
    rv = client.get("/posts/")
    assert rv.json["success"] == 1
    assert len(rv.json["posts"]) == 0, "We should have no posts"
    assert rv.json["meta"]["page_count"] == 0, "There should be no pages"


# def test_posts_post_not_on_main(client, post_not_on_main):
#     rv = client.get('/posts/')
#     assert rv.json['success'] == 1
#     assert len(rv.json['posts']) == 0, 'We should have no posts'
#     assert rv.json['meta']['page_count'] == 0, 'There should be no pages'


def test_posts_post_is_draft(client, draft_post):
    rv = client.get("/posts/")
    assert rv.json["success"] == 1
    assert len(rv.json["posts"]) == 0, "We should have no posts"
    assert rv.json["meta"]["page_count"] == 0, "There should be no pages"


def test_post(client, post):
    rv = client.get("/posts/" + post.url + "/")
    assert rv.json["success"] == 1
    assert "post" in rv.json, "We should have post"
    assert rv.json["post"]["title"] == post.title, "Wrong title"


def test_post_get_draft_not_auth(client, draft_post):
    rv = client.get("/posts/" + draft_post.url + "/")
    assert rv.json["success"] == 0
    assert "post" not in rv.json, "We should have no post"
    assert rv.json["error"]["code"] == 3


def test_post_get_draft_wrong_user(client, draft_post, reader_token):
    rv = client.get("/posts/" + draft_post.url + "/")
    assert rv.json["success"] == 0
    assert "post" not in rv.json, "We should have no post"
    assert rv.json["error"]["code"] == 3


def test_post_get_draft(client, draft_post, user_token):
    rv = client.get(
        "/posts/" + draft_post.url + "/", headers={"Authorization": user_token[1].token}
    )
    assert rv.json["success"] == 1
    assert "post" in rv.json, "We should have post"
    assert rv.json["post"]["title"] == draft_post.title, "Wrong title"


def test_create_post(client, user_token):
    rv = client.post(
        "/posts/",
        headers={"Authorization": user_token[1].token},
        json={"url": "sample-url"},
    )
    assert rv.json["success"] == 1
    assert "post" in rv.json, "No post in response"

    post = Post.get()
    assert post.creator == user_token[0], "Wrong creator"
    assert post.id == rv.json["post"]["id"]


def test_edit_post(client, post, user_token):
    rv = client.put(
        "/posts/" + post.url + "/",
        json={"title": "new title"},
        headers={"Authorization": user_token[1].token},
    )
    assert rv.json["success"] == 1

    assert Post.get().title == "new title", "Post title not chaged"


def test_edit_post_with_cut(client, post, user_token):
    rv = client.put(
        "/posts/" + post.url + "/",
        json={"text": '<p>Some text</p><cut name="it\'s cut"></cut><p>More text</p>"'},
        headers={"Authorization": user_token[1].token},
    )
    assert rv.json["success"] == 1

    assert Post.get().cut_text == "<p>Some text</p>"
    assert Post.get().cut_name == "it's cut"
    assert (
        Post.get().text
        == '<p>Some text</p><cut name="it\'s cut"></cut><p>More text</p>"'
    )


def test_edit_post_wrong_user(client, post, user_not_in_blog_with_token):
    rv = client.put(
        "/posts/" + post.url + "/",
        json={"title": "new title"},
        headers={"Authorization": user_not_in_blog_with_token[1].token},
    )
    assert rv.json["success"] == 0
    assert rv.json["error"]["code"] == 3

    assert Post.get().title == post.title, "Post title changed"
    assert Post.get().title != "new title"


def test_edit_post_reader(client, post, reader_token):
    rv = client.put(
        "/posts/" + post.url + "/",
        json={"title": "new title"},
        headers={"Authorization": reader_token[1].token},
    )

    assert rv.json["success"] == 0
    assert rv.json["error"]["code"] == 3

    assert Post.get().title == post.title, "Post title changed"
    assert Post.get().title != "new title"


def test_delete_post(client, post, user_token):
    rv = client.delete(
        "/posts/" + post.url + "/", headers={"Authorization": user_token[1].token}
    )
    assert rv.json["success"] == 1

    assert Post.select().count() == 0, "Post not deleted"


def test_delete_post_wrong_user(client, post, user_not_in_blog_with_token):
    rv = client.delete(
        "/posts/" + post.url + "/",
        headers={"Authorization": user_not_in_blog_with_token[1].token},
    )
    assert rv.json["success"] == 0
    assert rv.json["error"]["code"] == 3

    assert Post.select().count() == 1, "Post was deleted"


def test_delete_post_reader(client, post, reader_token):
    rv = client.delete(
        "/posts/" + post.url + "/", headers={"Authorization": reader_token[1].token}
    )
    assert rv.json["success"] == 0
    assert rv.json["error"]["code"] == 3

    assert Post.select().count() == 1, "Post was deleted"


def test_post_comments(client, post, comment):
    rv = client.get("/posts/" + post.url + "/comments/")
    assert rv.json["success"] == 1
    assert "comments" in rv.json, "We should have comments"
    assert rv.json["comments"][0]["text"] == comment.text, "Wrong title"


def test_post_send_comment(client, post, user_token):
    rv = client.post(
        "/posts/" + post.url + "/comments/",
        headers={"Authorization": user_token[1].token},
        json={"text": "This is comment"},
    )
    assert rv.json["success"] == 1

    assert Comment.select().count() == 1
    assert Comment.get().text == "This is comment"
