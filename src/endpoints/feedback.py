import datetime
from flask import Blueprint, jsonify, request, current_app
from src.model.models import Feedback, User, Notification
from src.telegram import Telegram
from src.auth import login_required, get_user_from_request
from src import errors
from src.trello import Trello

bp = Blueprint("feedback", __name__, url_prefix="/feedback/")


@bp.route("/", methods=["POST"])
@login_required
def leave_feedback():
    """Оставить отзыв"""
    json = request.get_json()
    if "text" in json:
        Feedback.create(text=json["text"], user=get_user_from_request())

        Telegram(current_app.config).notify_admin_channel(
            "Пользователь %s оставил отзыв: %s"
            % (get_user_from_request().username, json["text"])
        )

        success = Trello(current_app.config).create_card(json["text"])
        if not success:
            return errors.feedback_trello_error()

        for user in User.get_admins():
            Notification.create(
                user=user,
                created_date=datetime.datetime.now(),
                text="Пользователь %s оставил отзыв: %s"
                % (get_user_from_request().username, json["text"]),
                object_type="feedback",
            )

        return jsonify({"success": 1})
    else:
        return errors.wrong_payload("text")


@bp.route("/", methods=["GET"])
@login_required
def get_feedback():
    """Получить список отзывов"""
    user = get_user_from_request()
    if user.is_admin:
        return jsonify(
            {"success": 1, "feedback": [f.to_json() for f in Feedback.select()]}
        )
    else:
        return errors.no_access()


@bp.route("/<id>/", methods=["GET"])
@login_required
def resolve(id):
    """Пометить отзыв как решенный"""
    user = get_user_from_request()
    if user.is_admin:
        f = Feedback.get_or_none(Feedback.id == id)
        if f is None:
            return errors.not_found()

        f.is_resolved = True
        f.save()

        return jsonify({"success": 1})
    else:
        return errors.no_access()
