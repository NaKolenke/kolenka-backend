import datetime
from flask import Blueprint, jsonify
from src.auth import login_required, get_user_from_request
from src.model.models import User
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
