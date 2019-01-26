from flask import Blueprint, jsonify

bp = Blueprint('doc', __name__, url_prefix='/doc/')


class Endpoint:
    def __init__(self, method, url, section, description, body=None,
                 response=None, error_response=None, status='Available'):
        self.method = method
        self.url = url
        self.section = section
        self.description = description
        self.body = body
        self.response = response
        self.error_response = error_response
        self.status = status


@bp.route("/", methods=['GET'])
def documentation():
    endpoints = [
        Endpoint('GET', '/doc/', 'doc', 'Текущая документация.'),

        Endpoint('GET', '/users/', 'users',
                 'Получение списка пользователей. ' +
                 'Возможные параметры запроса: page - выбранная страница.'),
        Endpoint('GET', '/users/<id>/', 'users',
                 'Получение конкретного пользователя.'),
        Endpoint('GET', '/users/self/', 'users',
                 'Получение текущего пользователя. Необходима авторизация.'),
        Endpoint('POST', '/users/self/', 'users',
                 'Изменение текущего пользователя. Необходима авторизация. ' +
                 'Username изменить нельзя',
                 body={
                     'password': 'some_pass',
                     'email': 'aaa@Aaa',
                     'name': 'some name',
                     'about': 'some text',
                     'birthday': 1540368218,
                     'avatar': 32
                 }),

        Endpoint('GET', '/users/register/', 'users',
                 'Регистрация пользователя',
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
                 'Получение токена авторизации.'),
        Endpoint('GET', '/users/<id>/blogs/', 'users',
                 'Получение блогов пользователя.'),

        Endpoint('POST', '/tokens/valid/', 'token',
                 'Проверить, валиден ли токен.'),
        Endpoint('POST', '/tokens/refresh/', 'token', 'Обновить токен.'),

        Endpoint('GET', '/page/<name>/', 'page',
                 'Получить статью <name>.', status='Not available'),
        Endpoint('POST', '/page/<name>/', 'page',
                 'Обновить статью <name>. ' +
                 'Доступно только пользователям с ролью администратор.',
                 status='Not available'),

        Endpoint('POST', '/content/', 'content',
                 'Загрузить файл. В запросе необходимо передать поле file.'),
        Endpoint('GET', '/content/<id>/', 'content',
                 'Получить файл.'),

        Endpoint('POST', '/feedback/', 'feedback',
                 'Оставить отзыв. Необходима авторизация.'),
        Endpoint('GET', '/feedback/', 'feedback',
                 'Получить список отзывов. ' +
                 'Доступно только пользователям с ролью администратор.'),

        Endpoint('GET', '/blogs/', 'blogs',
                 'Получить список публичных блогов. ' +
                 'Возможные параметры запроса: page - выбранная страница.'),
        Endpoint('POST', '/blogs/', 'blogs',
                 'Создать новый блог'),
        Endpoint('PUT', '/blogs/<id>/', 'blogs',
                 'Редактировать блог'),
        Endpoint('DELETE', '/blogs/<id>/', 'blogs',
                 'Удалить блог'),
        Endpoint('GET', '/blogs/<id>/', 'blogs',
                 'Получение конкретного блога.'),
        Endpoint('GET', '/blogs/<id>/readers/', 'blogs',
                 'Получение читателей блога.'),
        Endpoint('POST', '/blogs/<id>/invite/', 'blogs',
                 'Отправить приглашение в блог.',
                 body={
                     'user': 45,
                     'role': 'owner or reader or writer'
                 },
                 response={
                     'success': 1,
                     'invite': 1
                 }),
        Endpoint('POST', '/blogs/<id>/invite/', 'blogs',
                 'Принять приглашение в блог.',
                 body={
                     'invite': 45
                 },
                 response={
                     'success': 1
                 }),

        Endpoint('GET', '/posts/', 'posts',
                 'Получение постов, главная страница.'),
        Endpoint('GET', '/posts/<url>/', 'posts',
                 'Получение одного поста'),
        Endpoint('POST', '/posts/', 'posts',
                 'Создать новый пост'),
        Endpoint('PUT', '/posts/<url>/', 'posts',
                 'Редактировать пост'),
        Endpoint('DELETE', '/posts/<url>/', 'posts',
                 'Удалить пост'),

        Endpoint('GET', '/posts/<url>/comments', 'posts',
                 'Получение списка комментариев к посту'),
        Endpoint('POST', '/posts/<url>/comments', 'posts',
                 'Отправка комментария'),

    ]

    return jsonify({
        'success': 1,
        'endpoints': [e.__dict__ for e in endpoints]
    })
