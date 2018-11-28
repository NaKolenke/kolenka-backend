import functools
import datetime
from flask import request, jsonify
from src.model.token import Token

def login_required(f):
    @functools.wraps(f)
    def decorated_function(**kwargs):
        msg = 'You should be authorized to use this endpoint'
        if 'Authorization' not in request.headers:
            return make_error(msg, 401)
        else:
            is_valid = False
            actual_token = get_token_from_request()
            if actual_token:
                if actual_token.valid_until > datetime.datetime.now():
                    is_valid = True
            
            if not is_valid:
                return make_error(msg, 401)

        return f(**kwargs)

    return decorated_function

def get_token_from_request():
    if 'Authorization' not in request.headers:
        return None
    token = request.headers['Authorization']
    actual_token = Token.get_or_none((Token.token==token) & (Token.is_refresh_token==False))
    return actual_token

def get_user_from_request():
    token = get_token_from_request()
    if token:
        return token.user
    return None

def make_error(message, code):
    response = jsonify({
        'success': 0,
        'error': message
    })
    response.status_code = code
    return response