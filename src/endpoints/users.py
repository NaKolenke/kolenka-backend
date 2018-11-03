import datetime
import hashlib
from flask import current_app, Blueprint, request, jsonify, abort
from playhouse.shortcuts import model_to_dict, dict_to_model
from src.model.user import User

bp = Blueprint('users', __name__, url_prefix='/users/')

@bp.route("/")
def users():
    users = []
    for u in User.select():
        users.append(model_to_dict(u))
    return jsonify(users)

@bp.route("/register/", methods=['POST'])
def register():
    json = request.get_json()

    errors = []

    if 'username' not in json:
        errors.append('"Username" not in request')
    if 'password' not in json:
        errors.append('"Password" not in request')
    if 'email' not in json:
        errors.append('"Email" not in request')
    if 'name' not in json:
        errors.append('"Name" not in request')

    if len(errors) > 0:
        message = ''
        for e in errors:
            message = message + e + ', '
        return make_error(message[0:-2], 400)

    username = json['username']
    password = json['password']
    email = json['email']
    name = json['name']

    user = User.get_or_none(User.login==username)
    if user is not None:
        return make_error('User with this username already created', 400)
    user = User.get_or_none(User.email==email)
    if user is not None:
        return make_error('User with this email already created', 400)

    user = User.create(login=username, password=salted(password, current_app.config['PASSWORD_SALT']), email=email, registration_date=datetime.datetime.now(), last_active_date=datetime.datetime.now(), name=name)

    return jsonify({
            'success': 1,
            'token': 1
            })

@bp.route("/login/", methods=['POST'])
def login():
    json = request.get_json()

    if not ('username' in json and 'password' in json):
        return make_error('Username or password not in request', 400)

    username = json['username']
    password = json['password']

    user = User.get_or_none(User.login==username)

    if user is not None and authorize(user, password):
        return jsonify({
            'success': 1,
            'token': 1
            })

    return make_error('Can\'t authorize', 401)

def authorize(user, password):
    if user.password == salted(password, current_app.config['PASSWORD_SALT']):
        return True
    return False

def salted(data, salt):
    return '0x:' + hashed(data + '::' + salt)

def hashed(data):
    bdata = data.encode()
    sha1 = hashlib.sha1(bdata).hexdigest().encode()
    return hashlib.md5(sha1).hexdigest()

def make_error(message, code):
    response = jsonify({
        'success': 0,
        'error': message
    })
    response.status_code = code
    return response
