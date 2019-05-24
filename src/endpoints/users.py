import datetime
import hashlib
from flask import current_app, Blueprint, request, jsonify
from playhouse.flask_utils import PaginatedQuery
from src.auth import login_required, get_user_from_request
from src.model.models import User, Token, Content, Blog, Post
from src import errors


bp = Blueprint('users', __name__, url_prefix='/users/')


@bp.route("/")
def users():
    query = User.select()
    limit = max(1, min(int(request.args.get('limit')) or 20, 100))
    paginated_query = PaginatedQuery(query, paginate_by=limit)

    return jsonify({
        'success': 1,
        'users': [u.to_json() for u in paginated_query.get_object_list()],
        'meta': {
            'page_count': paginated_query.get_page_count()
        }
    })


@bp.route("/<username>/")
def user(username):
    user = User.get_or_none(User.username == username)

    if user is None:
        return errors.not_found()

    return jsonify({
        'success': 1,
        'user': user.to_json(),
    })


@bp.route("/<username>/blogs/")
def user_blogs(username):
    user = User.get_or_none(User.username == username)

    if user is None:
        return errors.not_found()

    query = Blog.get_blogs_for_user(user)
    limit = max(1, min(int(request.args.get('limit')) or 20, 100))
    paginated_query = PaginatedQuery(query, paginate_by=limit)

    return jsonify({
        'success': 1,
        'blogs': [b.to_json() for b in paginated_query.get_object_list()],
        'meta': {
            'page_count': paginated_query.get_page_count()
        }
    })


@bp.route("/<username>/posts/")
def user_posts(username):
    user = User.get_or_none(User.username == username)

    if user is None:
        return errors.not_found()

    query = Post.get_user_posts(user)
    limit = max(1, min(int(request.args.get('limit')) or 20, 100))
    paginated_query = PaginatedQuery(query, paginate_by=limit)

    return jsonify({
        'success': 1,
        'posts': [p.to_json() for p in paginated_query.get_object_list()],
        'meta': {
            'page_count': paginated_query.get_page_count()
        }
    })


@bp.route("/drafts/")
@login_required
def user_drafts():
    user = get_user_from_request()

    query = Post.get_user_drafts(user)
    limit = max(1, min(int(request.args.get('limit')) or 20, 100))
    paginated_query = PaginatedQuery(query, paginate_by=limit)

    return jsonify({
        'success': 1,
        'posts': [p.to_json() for p in paginated_query.get_object_list()],
        'meta': {
            'page_count': paginated_query.get_page_count()
        }
    })


@bp.route("/self/", methods=['GET', 'POST'])
@login_required
def current_user():
    user = get_user_from_request()

    if request.method == 'POST':
        json = request.get_json()

        user.password = json.get('password', user.password)
        user.email = json.get('email', user.email)
        user.name = json.get('name', user.name)
        user.about = json.get('about', user.about)
        user.birthday = json.get('birthday', user.birthday)
        if 'avatar' in json:
            user.avatar = Content.get_or_none(Content.id == json['avatar'])

        user.save()

    user = User.get(User.id == user.id)

    return jsonify({
        'success': 1,
        'user': user.to_json_with_email()
    })


@bp.route("/register/", methods=['POST'])
def register():
    json = request.get_json()

    missed_payload = []

    if 'username' not in json:
        missed_payload.append('username')
    if 'password' not in json:
        missed_payload.append('password')
    if 'email' not in json:
        missed_payload.append('email')
    if 'name' not in json:
        missed_payload.append('name')

    if len(missed_payload) > 0:
        return errors.wrong_payload(missed_payload)

    username = json['username']
    password = json['password']
    email = json['email']
    name = json['name']

    user = User.get_or_none(User.username == username)
    if user is not None:
        return errors.registration_username_busy()
    user = User.get_or_none(User.email == email)
    if user is not None:
        return errors.registration_email_busy()

    user = User.create(
        username=username,
        password=salted(password, current_app.config['PASSWORD_SALT']),
        email=email,
        registration_date=datetime.datetime.now(),
        last_active_date=datetime.datetime.now(),
        name=name)

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


@bp.route("/login/", methods=['POST'])
def login():
    json = request.get_json()

    has_login = ('username' in json or 'email' in json)
    has_password = ('password' in json)
    if not has_login:
        return errors.wrong_payload('username', 'email')
    if not has_password:
        return errors.wrong_payload('password')

    user = None
    if 'username' in json:
        username = json['username']

        user = User.get_or_none(User.username == username)
        if user is None:
            user = User.get_or_none(User.email == username)
    elif 'email' in json:
        email = json['email']

        user = User.get_or_none(User.username == email)
        if user is None:
            user = User.get_or_none(User.email == email)

    password = json['password']

    if user is not None and authorize(user, password):
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

    return errors.not_authorized()


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
