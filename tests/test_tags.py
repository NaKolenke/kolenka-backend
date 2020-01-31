import datetime
import pytest
from src.model.models import Tag, TagMark


@pytest.fixture
def tag(post):
    tag = Tag.create(created_date=datetime.datetime.now(), title=u"тэг",)

    TagMark.create(tag=tag, post=post)

    from src.model import db

    db.db_wrapper.database.close()

    return tag


@pytest.fixture
def tag_no_post():
    tag = Tag.create(created_date=datetime.datetime.now(), title=u"тэг",)

    from src.model import db

    db.db_wrapper.database.close()

    return tag


def test_tags(client, tag):
    rv = client.get("/tags/")
    assert rv.json["success"] == 1
    assert len(rv.json["tags"]) == 1, "We should have only one tag"
    assert rv.json["tags"][0]["title"] == tag.title, "Wrong title"
    assert rv.json["meta"]["page_count"] == 1, "There should be one page"


def test_tags_no_post(client, tag_no_post):
    rv = client.get("/tags/")
    assert rv.json["success"] == 1
    assert len(rv.json["tags"]) == 1, "We should have only one tag"
    assert rv.json["tags"][0]["title"] == tag_no_post.title, "Wrong title"
    assert rv.json["meta"]["page_count"] == 1, "There should be one page"


def test_no_tags(client):
    rv = client.get("/tags/")
    assert rv.json["success"] == 1
    assert len(rv.json["tags"]) == 0, "We should have no tags"
    assert rv.json["meta"]["page_count"] == 0, "There should be no pages"


def test_tag(client, tag, post):
    rv = client.get("/tags/" + tag.title + "/")
    assert rv.json["success"] == 1
    assert len(rv.json["posts"]) == 1, "We should have only one post"
    assert rv.json["posts"][0]["title"] == post.title, "Wrong title"
    assert rv.json["meta"]["page_count"] == 1, "There should be one page"


def test_suggestions(client, tag):
    rv = client.post("/tags/suggestion/", json={"title": u"тэ"})
    assert rv.json["success"] == 1
    assert len(rv.json["tags"]) == 1, "We should have only one tag"
    assert rv.json["tags"][0]["title"] == tag.title, "Wrong title"

    rv = client.post("/tags/suggestion/", json={"title": "ta"})
    assert rv.json["success"] == 1
    assert len(rv.json["tags"]) == 0, "We should have no tags"
