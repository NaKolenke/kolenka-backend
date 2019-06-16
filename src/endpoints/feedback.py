from flask import Blueprint, jsonify, request, current_app
from src.model.models import Feedback
from src.telegram import Telegram
from src.auth import login_required, get_user_from_request
from src import errors
from urllib import request as lib_request
from urllib.parse import urlencode
import json as lib_json

bp = Blueprint('feedback', __name__, url_prefix='/feedback/')


@bp.route("/", methods=['POST'])
@login_required
def leave_feedback():
    '''Оставить отзыв'''
    json = request.get_json()
    if 'text' in json:
        Feedback.create(text=json['text'], user=get_user_from_request())

        Telegram(current_app.config).notify_admin_channel(
            'Пользователь %s оставил отзыв: %s' %
            (get_user_from_request().username, json['text']))

        res_body = None

        if current_app.config['TRELLO_KEY'] and current_app.config['TRELLO_TOKEN']:
            query = urlencode({
                'key': current_app.config['TRELLO_KEY'],
                'token': current_app.config['TRELLO_TOKEN'],
                'idList': current_app.config['TRELLO_LIST_ID']
            })

            text = json['text']

            req = lib_request.Request('https://api.trello.com/1/cards?' + query, lib_json.dumps({
                'name': text[:128] + ('...' if len(text) > 128 else ''),
                'desc': text
            }).encode('utf-8'), {
                'Content-Type': 'application/json; charset=utf-8'
            })
            res = lib_request.urlopen(req)

            if res.getcode() != 200:
                return jsonify({
                    'success': 0,
                    'error': {
                        'code': -1,
                        'message': 'Something went wrong with Trello service'
                    }
                })

            res_body = lib_json.load(res)

        return jsonify({
            'success': 1,
            'response': res_body
        })
    else:
        return errors.wrong_payload('text')


@bp.route("/", methods=['GET'])
@login_required
def get_feedback():
    '''Получить список отзывов'''
    user = get_user_from_request()
    if user.is_admin:
        return jsonify({
            'success': 1,
            'feedback': [f.to_json() for f in Feedback.select()]
        })
    else:
        return errors.no_access()


@bp.route("/<id>/", methods=['GET'])
@login_required
def resolve(id):
    '''Пометить отзыв как решенный'''
    user = get_user_from_request()
    if user.is_admin:
        f = Feedback.get_or_none(Feedback.id == id)
        if f is None:
            return errors.not_found()

        f.is_resolved = True
        f.save()

        return jsonify({
            'success': 1
        })
    else:
        return errors.no_access()
