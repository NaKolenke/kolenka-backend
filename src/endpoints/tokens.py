import datetime
from flask import Blueprint, request, jsonify
from src.model.models import Token
from src import errors

bp = Blueprint('tokens', __name__, url_prefix='/token/')


@bp.route("/validate/", methods=['POST'])
def valid():
    json = request.get_json()

    if 'token' not in json:
        return errors.wrong_payload('token')

    token = json['token']

    actual_token = Token.get_or_none(
        (Token.token == token) &
        (Token.is_refresh_token == False))  # noqa: E712

    if actual_token is None:
        return errors.token_invalid()

    if actual_token.valid_until < datetime.datetime.now():
        return errors.token_outdated()

    return jsonify({
            'success': 1
        })


@bp.route("/refresh/", methods=['POST'])
def refresh():
    json = request.get_json()

    if 'token' not in json:
        return errors.wrong_payload('token')

    token = json['token']

    actual_token = Token.get_or_none(
        (Token.token == token) &
        (Token.is_refresh_token == True))  # noqa: E712

    if actual_token is None:
        return errors.token_invalid()

    if actual_token.valid_until < datetime.datetime.now():
        return errors.token_outdated()

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
