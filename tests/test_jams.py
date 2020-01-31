import datetime
from datetime import timedelta
import pytest
from src.model.models import Blog, BlogParticipiation, Jam


@pytest.fixture
def jam(user, reader_token):
    jam_title = "test jam"
    jam_url = "test-jam"

    blog = Blog.create(
        title="test_blog",
        url="test_blog",
        creator=user,
        created_date=datetime.datetime.now(),
        updated_date=datetime.datetime.now(),
    )
    BlogParticipiation.create(blog=blog, user=user, role=1)

    blog.title = jam_title
    blog.description = f'Это блог для джема "{jam_title}"'
    blog.url = jam_url
    blog.blog_type = 1
    blog.save()

    jam = Jam.create(
        created_date=datetime.datetime.now(),
        updated_date=datetime.datetime.now(),
        creator=user,
        blog=blog,
        title=jam_title,
        url=jam_url,
        description="some description without tags",
        short_description="short description",
        start_date=datetime.datetime.now() + timedelta(seconds=1),
        end_date=datetime.datetime.now() + timedelta(seconds=5),
    )

    from src.model import db

    db.db_wrapper.database.close()

    return jam


def test_jams(client, jam):
    rv = client.get("/blogs/")
    assert rv.json["success"] == 1
    assert len(rv.json["blogs"]) == 1, "We should have only one blog"
    assert rv.json["blogs"][0]["title"] == jam.title
    assert rv.json["blogs"][0]["readers"] == 1, "Wrong count of readers"
    assert rv.json["meta"]["page_count"] == 1

    rv = client.get("/jams/")
    assert rv.json["success"] == 1
    assert len(rv.json["jams"]) == 1, "We should have only one jam"
    assert rv.json["jams"][0]["title"] == jam.title
    assert rv.json["meta"]["page_count"] == 1, "There should be one page"


def test_create_jam(client, user_token):
    rv = client.post(
        "/jams/",
        headers={"Authorization": user_token[1].token},
        json={
            "title": "test title for jam",
            "url": "test-jam",
            "description": "description",
            "short_description": "short",
            "start_date": datetime.datetime.now().timestamp() + 5,
            "end_date": datetime.datetime.now().timestamp() + 10,
        },
    )
    assert rv.json["success"] == 1
    assert "jam" in rv.json

    blog = Blog.get()
    assert blog.creator == user_token[0], "Wrong creator"
    assert blog.description == 'Это блог для джема "test title for jam"'

    participiation = BlogParticipiation.get()
    assert participiation.user == user_token[0]
    assert participiation.role == 1, "Not owner on creation"

    jam = Jam.get()
    assert jam.creator == user_token[0], "Wrong creator"
    assert jam.title == "test title for jam"
    assert jam.url == "test-jam"
    assert jam.description == "description"
    assert jam.short_description == "short"
    assert int(jam.start_date) > int(datetime.datetime.now().timestamp())
    assert int(jam.start_date) == int(jam.end_date - 5)


def test_edit_jam(client, user_token, jam):
    rv = client.post(
        f"/jams/{jam.id}/",
        headers={"Authorization": user_token[1].token},
        json={"title": "new title"},
    )
    assert rv.json["success"] == 1
    assert "jam" in rv.json

    blog = Blog.get()
    assert blog.creator == user_token[0], "Wrong creator"
    assert blog.description == 'Это блог для джема "new title"'

    participiation = BlogParticipiation.get()
    assert participiation.user == user_token[0]
    assert participiation.role == 1, "Not owner on creation"

    jam = Jam.get()
    assert jam.creator == user_token[0], "Wrong creator"
    assert jam.title == "new title"
    assert jam.url == jam.url
    assert jam.description == jam.description
    assert jam.short_description == jam.short_description


def test_edit_jam_not_creator(client, user_token, jam, reader_token):
    rv = client.post(
        f"/jams/{jam.id}/",
        headers={"Authorization": reader_token[1].token},
        json={"title": "new title"},
    )

    assert rv.json["success"] == 0
    assert rv.json["error"]["code"] == 3

    jam = Jam.get()
    assert jam.title == jam.title
