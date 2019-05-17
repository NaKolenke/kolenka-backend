import datetime
import hashlib
from flask import current_app, Blueprint, request, jsonify
from playhouse.shortcuts import model_to_dict
from playhouse.flask_utils import PaginatedQuery
from src.auth import login_required, get_user_from_request
from src.model.models import User, Token, Content, Blog, Post
from src.utils import make_error, send_error
from src.errors import error_not_found, error_no_access


bp = Blueprint('users', __name__, url_prefix='/users/')


public_exclude = [ User.password, User.email ]


@bp.route("/")
def users():
    users = []
    query = User.select()
    paginated_query = PaginatedQuery(query, paginate_by=20)

    for u in paginated_query.get_object_list():
        users.append(model_to_dict(
            u, exclude=public_exclude + [User.birthday, User.about]
        ))

    return jsonify({
        'success': 1,
        'users': users,
        'meta': {
            'page_count': paginated_query.get_page_count()
        }
    })


@bp.route("/<username>/")
def user(username):
    user = User.get_or_none(User.username == username)

    if user is None:
        return send_error(error_not_found, 404)

    return jsonify({
        'success': 1,
        'user': model_to_dict(user, exclude=public_exclude),
    })


@bp.route("/<username>/blogs/")
def user_blogs(username):
    user = User.get_or_none(User.username == username)

    if user is None:
        return send_error(error_not_found, 404)

    blogs = []
    query = Blog.get_blogs_for_user(user)
    paginated_query = PaginatedQuery(query, paginate_by=20)

    for b in paginated_query.get_object_list():
        blogs.append(model_to_dict(b, exclude=public_exclude))

    return jsonify({
        'success': 1,
        'blogs': blogs,
        'meta': {
            'page_count': paginated_query.get_page_count()
        }
    })


@bp.route("/<username>/posts/")
def user_posts(username):
    user = User.get_or_none(User.username == username)

    if user is None:
        return send_error(error_not_found, 404)

    posts = []
    query = Post.get_posts_for_user(user)
    paginated_query = PaginatedQuery(query, paginate_by=10)
    
    for p in paginated_query.get_object_list():
        posts.append(model_to_dict(p, exclude=public_exclude))

    return jsonify({
        'success': 1,
        'posts': posts,
        'meta': {
            'page_count': paginated_query.get_page_count()
        }
    })


@bp.route("/drafts/")
def user_drafts(username):
    user = get_user_from_request()

    if user is None:
        return send_error(error_no_access, 404)

    user = User.get(User.id == user.id)

    query = Post.get_drafts_for_user(user)
    paginated_query = PaginatedQuery(query, paginate_by=10)

    posts = list(map(
        lambda x: model_to_dict(x, exclude=public_exclude), 
        paginated_query.get_object_list()
    ))

    return jsonify({
        'success': 1,
        'posts': posts,
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
        'user': model_to_dict(user, exclude=[User.password])
    })


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

    user = User.get_or_none(User.username == username)
    if user is not None:
        return make_error('User with this username already created', 400)
    user = User.get_or_none(User.email == email)
    if user is not None:
        return make_error('User with this email already created', 400)

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
        return make_error('Username or email not in request', 400)
    if not has_password:
        return make_error('Password not in request', 400)

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
