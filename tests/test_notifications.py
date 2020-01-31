from src.model.models import Notification


def test_notifications(client, user_token):
    rv = client.get("/notifications/", headers={"Authorization": user_token[1].token})
    assert rv.json["success"] == 1
    assert len(rv.json["notifications"]) == 0

    rv = client.get(
        "/notifications/test", headers={"Authorization": user_token[1].token}
    )
    assert rv.json["success"] == 1
    assert Notification.select().count() == 1
    from src.model import db

    db.db_wrapper.database.close()

    rv = client.get("/notifications/", headers={"Authorization": user_token[1].token})
    assert rv.json["success"] == 1
    assert len(rv.json["notifications"]) == 1
    assert "text" in rv.json["notifications"][0]
    assert rv.json["notifications"][0]["is_new"]

    rv = client.put(
        "/notifications/",
        headers={"Authorization": user_token[1].token},
        json={"ids": [rv.json["notifications"][0]["id"]]},
    )
    assert rv.json["success"] == 1

    rv = client.get("/notifications/", headers={"Authorization": user_token[1].token})
    assert rv.json["success"] == 1
    assert len(rv.json["notifications"]) == 1
    assert "text" in rv.json["notifications"][0]
    assert not rv.json["notifications"][0]["is_new"]

    rv = client.get(
        "/notifications/test", headers={"Authorization": user_token[1].token}
    )
    assert rv.json["success"] == 1
    assert Notification.select().count() == 2
    from src.model import db

    db.db_wrapper.database.close()

    rv = client.get(
        "/notifications/new", headers={"Authorization": user_token[1].token}
    )
    assert rv.json["success"] == 1
    assert len(rv.json["notifications"]) == 1
    assert "text" in rv.json["notifications"][0]
    assert rv.json["notifications"][0]["is_new"]

    rv = client.get("/notifications/", headers={"Authorization": user_token[1].token})
    assert rv.json["success"] == 1
    assert len(rv.json["notifications"]) == 2
