from flask import Blueprint, jsonify

bp = Blueprint('doc', __name__, url_prefix='/doc/')


class Endpoint:
    def __init__(self, method, url, section, description, body='', response='', error_response='', status='Available'):
        self.method = method
        self.url = url
        self.section = section
        self.description = description
        self.body = body
        self.response = response
        self.error_response = error_response
        self.status = status


@bp.route("/", methods=['GET'])
def valid():
    endpoints = [
        Endpoint('GET', '/doc/', 'doc', 'Текущая документация'),

        Endpoint('GET', '/users/', 'users',
                 'Получение списка пользователей. Возможные параметры запроса: page - выбранная страница.'),
        Endpoint('GET', '/users/<id>/', 'users',
                 'Получение конкретного пользователя', status='Not available'),

        Endpoint('GET', '/users/register/', 'users', 'Регистрация пользователя', 
        body={
            'username': 'test_user',
            'password': 'some-pass',
            'name': 'name',
            'email': 'email',
        }, 
        response={
            'success': 1,
            'access_token': {
                'token': 'aaa',
                'valid_until': 1540368218
            },
            'refresh_token': {
                'token': 'aaa',
                'valid_until': 1540368218
            },
        },
        error_response={
            'success': 0,
            'error': 'Error message'
        }
        ),
        Endpoint('GET', '/users/login/', 'users',
                 'Получение токена авторизации'),

        Endpoint('POST', '/tokens/valid/', 'token',
                 'Проверить, валиден ли токен'),
        Endpoint('POST', '/tokens/refresh/', 'token', 'Обновить токен'),

        Endpoint('GET', '/page/<name>/', 'page',
                 'Получить статью <name>', status='Not available'),
        Endpoint('POST', '/page/<name>/', 'page',
                 'Обновить статью <name>. Доступно только пользователям с ролью вдминистратор', status='Not available'),

    ]

    return jsonify({
        'success': 1,
        'endpoints': [e.__dict__ for e in endpoints]
    })


def add_endpoint(endpoints, name, description):
    endpoints.append({
        'name': name,
        'description': description
    })
