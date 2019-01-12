from flask import Blueprint, jsonify, request, current_app
from playhouse.shortcuts import model_to_dict
from src.model.models import Feedback
from src.telegram import Telegram
from src.auth import login_required, get_user_from_request
from src.utils import make_error

bp = Blueprint('feedback', __name__, url_prefix='/feedback/')


@bp.route("/", methods=['POST'])
@login_required
def leave_feedback():
    json = request.get_json()
    if 'text' in json:
        Feedback.create(text=json['text'], user=get_user_from_request())

        Telegram(current_app.config).notify_admin_channel('Пользователь ' + get_user_from_request().login + ' оставил отзыв: ' + json['text'])

        return jsonify({
            'success': 1
        })
    else:
        return make_error('No text provided')


@bp.route("/", methods=['GET'])
@login_required
def get_feedback():
    user = get_user_from_request()
    if user.role == 2:
        feedback = []
        for f in Feedback.select():
            feedback.append(model_to_dict(f))

        return jsonify({
            'success': 1,
            'feedback': feedback
        })
    else:
        return make_error('Current user doesn\'t have rights to this action')


@bp.route("/<id>/", methods=['GET'])
@login_required
def resolve(id):
    user = get_user_from_request()
    if user.role == 2:
        f = Feedback.get(id)
        f.is_resolved = True
        f.save()

        return jsonify({
            'success': 1
        })
    else:
        return make_error('Current user doesn\'t have rights to this action')
