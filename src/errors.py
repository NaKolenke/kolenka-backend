# flake8: noqa
from flask import jsonify


def prepare_error(error_code, error_message, response_code):
    response = jsonify({
        'success': 0,
        'error': {
            'code': error_code,
            'message': error_message
        }
    })
    response.status_code = response_code
    return response


def not_authorized(): return prepare_error(1, 'Not authorized', 401)
def no_access(): return prepare_error(3, 'No access', 403)
def not_found(): return prepare_error(4, 'Not found', 404)

def wrong_payload(*field_names):
    message = ''
    for f in field_names:
        message = message + 'No field "%s" specified, ' % f
    return prepare_error(5, message[0:-2], 400)


def token_invalid(): return prepare_error(10, 'Token is invalid', 400)
def token_outdated(): return prepare_error(11, 'Token is outdated', 400)

def registration_email_busy():
    return prepare_error(12, 'User with this email already created', 400)
def registration_username_busy():
     return prepare_error(13, 'User with this username already created', 400)

def pass_recover_no_user():
     return prepare_error(14, 'There is no user with specified email', 400)

def pass_recover_wrong_token():
     return prepare_error(15, 'Wrong token', 400)

def invite_not_found(): return prepare_error(20, 'Invite not found', 404)
def invite_wrong_role(): return prepare_error(21, 'Wrong role specified', 400)

def content_no_file(): return prepare_error(30, 'No "file"', 400)
def content_forbidden_extension(): return prepare_error(31, 'This file extension is not allowed', 400)
def content_file_size_exceeded(): return prepare_error(32, 'Size of the file is too big', 400)

def blog_no_access(): return prepare_error(40, 'No access to blog', 400)
def blog_not_found(): return prepare_error(41, 'Blog not found', 400)

def post_url_already_taken() : return prepare_error(50, 'A post with this url already exists', 400)

def feedback_trello_error(): return prepare_error(60, 'Cannot connect to trello', 500)

def user_avatar_is_not_image(): return prepare_error(70, 'Avatar is not an image', 400)
def user_avatar_too_large(): return prepare_error(71, 'Avatar too large', 400)

def sticker_is_not_image(): return prepare_error(80, 'Sticker is not an image', 400)
def sticker_too_large(): return prepare_error(81, 'Sticker too large', 400)

def vote_no_target(): return prepare_error(90, 'No target for vote', 400)
def vote_no_target_type(): return prepare_error(91, 'Invalid target type', 400)
