import datetime
from flask import Blueprint, jsonify, request
import peewee
from src.auth import login_required, get_user_from_request
from src.model.models import User, Content, Achievement, AchievementUser
from src import errors


bp = Blueprint("admin", __name__, url_prefix="/admin/")


@bp.route("/", methods=["GET"])
@login_required
def dashboard():
    """Получить статистику по сайту"""
    user = get_user_from_request()

    if not user.is_admin:
        return errors.no_access()

    users = User.select().count()

    d = datetime.datetime.now() - datetime.timedelta(days=7)
    active_users = User.select().where(User.last_active_date > d).count()
    return jsonify({"success": 1, "users": users, "active_users_7_days": active_users})


@bp.route("/achievements/", methods=["GET"])
def get_achievements():
    """Получить список наград"""
    achievements = Achievement.select()

    achievements = [a.to_json() for a in achievements]
    for a in achievements:
        users = (
            User.select(User.id, User.username)
            .join(AchievementUser, peewee.JOIN.LEFT_OUTER)
            .where(AchievementUser.achievement == a["id"])
        )

        a["users"] = [u.to_json() for u in users]

    return jsonify({"success": 1, "achievements": achievements})


@bp.route("/achievements/", methods=["POST"])
@login_required
def add_achievement():
    user = get_user_from_request()

    if not user.is_admin:
        return errors.no_access()

    json = request.get_json()

    if "title" not in json or "image" not in json:
        return errors.wrong_payload("title", "image")

    if len(json["title"]) == 0:
        return errors.wrong_payload("title")

    content = Content.get_or_none(Content.id == json["image"])
    if content:
        if not content.is_image:
            return errors.achievement_is_not_image()
        elif not content.is_small_image:
            return errors.achievement_too_large()

    achievement = Achievement.create(title=json["title"], image=content)

    return jsonify({"success": 1, "achievement": achievement.to_json()})


@bp.route("/achievements/assign/", methods=["POST"])
@login_required
def assign_achievement():
    user = get_user_from_request()

    if not user.is_admin:
        return errors.no_access()

    json = request.get_json()

    if "users" not in json or "achievement" not in json:
        return errors.wrong_payload("users", "achievement")

    if len(json["users"]) == 0:
        return errors.wrong_payload("users")

    achievement = Achievement.get_or_none(Achievement.id == json["achievement"])
    if achievement is None:
        return errors.wrong_payload("achievement")

    assign_errors = []
    for u in json["users"]:
        user_to_assign = User.get_or_none(User.id == u)
        if user_to_assign is None:
            assign_errors.append(f"Cannot assign achievement to user {u}")
        else:
            AchievementUser.create(
                achievement=achievement,
                user=user_to_assign,
                comment=json.get("comment", None),
            )

    return jsonify({"success": 1, "errors": assign_errors})


@bp.route("/achievements/unassign/", methods=["POST"])
@login_required
def unassign_achievement():
    user = get_user_from_request()

    if not user.is_admin:
        return errors.no_access()

    json = request.get_json()

    if "users" not in json or "achievement" not in json:
        return errors.wrong_payload("users", "achievement")

    if len(json["users"]) == 0:
        return errors.wrong_payload("users")

    achievement = Achievement.get_or_none(Achievement.id == json["achievement"])
    if achievement is None:
        return errors.wrong_payload("achievement")

    assign_errors = []
    for u in json["users"]:
        user = User.get_or_none(user.id == u)
        if user is None:
            assign_errors.append(f"Cannot unassign achievement from user {u}")
        else:
            assign = AchievementUser.get_or_none(achievement=achievement, user=user)
            assign.delete_instance()

    return jsonify({"success": 1, "errors": assign_errors})
