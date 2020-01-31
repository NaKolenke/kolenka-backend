def test_vote_post(client, post, user_token):
    rv = client.get("/posts/" + post.url + "/")
    assert rv.json["success"] == 1
    assert "post" in rv.json, "We should have post"
    assert rv.json["post"]["rating"] == 0, "Should have zero rating"

    rv = client.post(
        "/votes/",
        json={"target_id": rv.json["post"]["id"], "target_type": "post", "value": 1},
        headers={"Authorization": user_token[1].token},
    )

    rv = client.get(
        "/posts/" + post.url + "/", headers={"Authorization": user_token[1].token}
    )
    assert rv.json["success"] == 1
    assert "post" in rv.json, "We should have post"
    assert rv.json["post"]["rating"] == 1, "Should have rating 1"
    assert rv.json["post"]["user_voted"] == 1, "Should have tracked user vote"

    rv = client.post(
        "/votes/",
        json={"target_id": rv.json["post"]["id"], "target_type": "post", "value": 0},
        headers={"Authorization": user_token[1].token},
    )

    rv = client.get(
        "/posts/" + post.url + "/", headers={"Authorization": user_token[1].token}
    )
    assert rv.json["success"] == 1
    assert "post" in rv.json, "We should have post"
    assert rv.json["post"]["rating"] == 0, "Should have rating 0"
    assert rv.json["post"]["user_voted"] == 0, "Should have resetted user vote"
