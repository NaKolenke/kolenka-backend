import datetime
import hashlib
from flask import current_app, Blueprint, request, jsonify
from playhouse.flask_utils import PaginatedQuery
from src.auth import login_required, get_user_from_request
from src.model.models import User, Token, Content, Blog, Post, Vote
from src import errors
from src.email import EmailSender
from src.utils import sanitize, doc_sample


bp = Blueprint('users', __name__, url_prefix='/users/')


@bp.route("/")
def users():
    '''Получить список пользователей'''
    query = User.get_users_sorted_by_active_date()
    limit = max(1, min(int(request.args.get('limit') or 20), 100))
    paginated_query = PaginatedQuery(query, paginate_by=limit)

    users = [u.to_json() for u in paginated_query.get_object_list()]
    users = [Vote.add_votes_info(u, 1, get_user_from_request()) for u in users]

    return jsonify({
        'success': 1,
        'users': users,
        'meta': {
            'page_count': paginated_query.get_page_count()
        }
    })


@bp.route("/<username>/")
def user(username):
    '''Получить подробную информацию о пользователе'''
    user = User.get_or_none(User.username == username)

    if user is None:
        return errors.not_found()

    user_dict = user.to_json()
    user_dict = Vote.add_votes_info(user_dict, 1, get_user_from_request())

    return jsonify({
        'success': 1,
        'user': user_dict,
    })


@bp.route("/<username>/blogs/")
def user_blogs(username):
    '''Получить список блогов пользователя'''
    user = User.get_or_none(User.username == username)

    if user is None:
        return errors.not_found()

    query = Blog.get_blogs_for_user(user)
    limit = max(1, min(int(request.args.get('limit') or 20), 100))
    paginated_query = PaginatedQuery(query, paginate_by=limit)

    blogs = [b.to_json() for b in paginated_query.get_object_list()]
    blogs = [Vote.add_votes_info(b, 2, get_user_from_request()) for b in blogs]

    return jsonify({
        'success': 1,
        'blogs': blogs,
        'meta': {
            'page_count': paginated_query.get_page_count()
        }
    })


@bp.route("/<username>/posts/")
def user_posts(username):
    '''Получить список постов пользователя'''
    user = User.get_or_none(User.username == username)

    if user is None:
        return errors.not_found()

    query = Post.get_user_posts(user)
    limit = max(1, min(int(request.args.get('limit') or 20), 100))
    paginated_query = PaginatedQuery(query, paginate_by=limit)

    posts = [p.to_json() for p in paginated_query.get_object_list()]
    posts = [Vote.add_votes_info(p, 3, get_user_from_request()) for p in posts]

    return jsonify({
        'success': 1,
        'posts': posts,
        'meta': {
            'page_count': paginated_query.get_page_count()
        }
    })


@bp.route("/drafts/")
@login_required
def user_drafts():
    '''Получить список черновиков'''
    user = get_user_from_request()

    query = Post.get_user_drafts(user)
    limit = max(1, min(int(request.args.get('limit') or 20), 100))
    paginated_query = PaginatedQuery(query, paginate_by=limit)

    posts = [p.to_json() for p in paginated_query.get_object_list()]
    posts = [Vote.add_votes_info(p, 3, get_user_from_request()) for p in posts]

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
    '''Получить текущего пользователя или отредактировать профиль'''
    user = get_user_from_request()

    if request.method == 'POST':
        json = request.get_json()

        user.email = json.get('email', user.email)
        user.name = json.get('name', user.name)
        user.about = sanitize(json.get('about', user.about))
        user.birthday = json.get('birthday', user.birthday)
        if 'avatar' in json:
            content = Content.get_or_none(Content.id == json['avatar'])
            if content:
                if not content.is_image:
                    return errors.user_avatar_is_not_image()
                elif content.size > 1024 * 500:  # 500kb
                    return errors.user_avatar_too_large()
                else:
                    user.avatar = content

        user.save()

    user = User.get(User.id == user.id)

    return jsonify({
        'success': 1,
        'user': user.to_json_with_email()
    })


@bp.route("/register/", methods=['POST'])
def register():
    '''Регистрация'''
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
    '''Авторизация'''
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


@bp.route("/recover-password/", methods=['POST'])
@doc_sample(body={'email': 'email'})
def recover_pass():
    '''Сделать запрос на восстановление пароля'''
    json = request.get_json()

    if 'email' not in json:
        return errors.wrong_payload('email')

    user = User.get_or_none(User.email == json['email'])
    if user is None:
        return errors.pass_recover_no_user()

    t = Token.generate_recover_token(user)

    url = current_app.config['HOSTNAME'] + '/recover-pass?token=' + t.token

    sender = EmailSender(current_app.config)
    sender.recover_pass(url, user)

    return jsonify({
        'success': 1
    })


@bp.route("/new-password/", methods=['POST'])
@doc_sample(body={'token': 'token', 'password': 'new password'})
def new_pass():
    '''Поменять пароль'''
    json = request.get_json()

    if 'token' not in json:
        return errors.wrong_payload('token')
    if 'password' not in json:
        return errors.wrong_payload('password')

    token = Token.get_or_none(Token.token == json['token'])
    if token is None:
        return errors.pass_recover_wrong_token()
    if token.valid_until < datetime.datetime.now():
        return errors.token_outdated()

    user = token.user

    password = json['password']
    user.password = salted(password, current_app.config['PASSWORD_SALT'])
    user.save()

    token.delete_instance()

    return jsonify({
        'success': 1
    })


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
