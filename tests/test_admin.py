import pytest
from src.model.models import (
    AchievementUser,
    Achievement,
)


@pytest.fixture
def achievement(user):
    achievement = Achievement.create(title="test achievement", image=None)
    AchievementUser.create(achievement=achievement, user=user, comment="some comment")

    from src.model import db

    db.db_wrapper.database.close()

    return achievement


def test_get_achievements(client, user, achievement):
    rv = client.get("/admin/achievements/")
    assert rv.json["success"] == 1

    assert rv.json["achievements"][0]["title"] == achievement.title
    assert rv.json["achievements"][0]["users"][0]["username"] == user.username
