import functools
import datetime
from flask import request
from src.model.models import Token
from src import errors


def login_required(f):
    @functools.wraps(f)
    def decorated_function(**kwargs):
        if 'Authorization' not in request.headers:
            return errors.not_authorized()
        else:
            is_valid = False
            actual_token = get_token_from_request()
            if actual_token:
                if actual_token.valid_until > datetime.datetime.now():
                    is_valid = True

            if not is_valid:
                return errors.token_invalid()

        return f(**kwargs)

    return decorated_function


def get_token_from_request():
    if 'Authorization' not in request.headers:
        return None
    token = request.headers['Authorization']
    actual_token = Token.get_or_none(
        (Token.token == token) &
        (Token.token_type == 'access'))
    return actual_token


def get_user_from_request():
    token = get_token_from_request()
    if token:
        return token.user
    return None
