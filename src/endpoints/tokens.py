import datetime
from flask import Blueprint, request, jsonify
from src.model.models import Token
from src.utils import make_error

bp = Blueprint('tokens', __name__, url_prefix='/token/')


@bp.route("/validate/", methods=['POST'])
def valid():
    json = request.get_json()

    errors = []

    if 'token' not in json:
        errors.append('"Token" not in request')

    if len(errors) > 0:
        message = ''
        for e in errors:
            message = message + e + ', '
        return make_error(message[0:-2], 400)

    token = json['token']

    actual_token = Token.get_or_none(
        (Token.token == token) &
        (Token.is_refresh_token == False))  # noqa: E712

    if actual_token is None:
        return make_error('Token is invalid', 400)

    if actual_token.valid_until < datetime.datetime.now():
        return make_error('Token is outdated', 400)

    return jsonify({
            'success': 1
        })


@bp.route("/refresh/", methods=['POST'])
def refresh():
    json = request.get_json()

    errors = []

    if 'token' not in json:
        errors.append('"Token" not in request')

    if len(errors) > 0:
        message = ''
        for e in errors:
            message = message + e + ', '
        return make_error(message[0:-2], 400)

    token = json['token']

    actual_token = Token.get_or_none(
        (Token.token == token) &
        (Token.is_refresh_token == True))  # noqa: E712

    if actual_token is None:
        return make_error('Token is invalid', 400)

    if actual_token.valid_until < datetime.datetime.now():
        return make_error('Token is outdated', 400)

    user = actual_token.user

    token = Token.generate_access_token(user)
    refresh_token = Token.generate_refresh_token(user)

    return jsonify({
            'success': 1,
            'access_token': {
                'token': token.token,
                'valid_until': token.valid_until.timestamp(),
            },
            'refresh_token': {
                'token': refresh_token.token,
                'valid_until': refresh_token.valid_until.timestamp(),
            }
        })
