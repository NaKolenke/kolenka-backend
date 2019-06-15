import inspect
from flask import Blueprint, jsonify, current_app
from flask.json import loads
from src import errors as error_funcs

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
    '''Текущая документация'''
    endpoints = []
    for rule in current_app.url_map.iter_rules():
        # exclude HEAD and OPTIONS from list
        methods = [item for item in rule.methods
                   if item not in ['HEAD', 'OPTIONS']]
        method = str(methods)
        if len(methods) == 1:
            method = methods[0]

        url = rule.rule
        section = rule.endpoint[:rule.endpoint.find('.')]

        func = current_app.view_functions[rule.endpoint]
        doc = func.__doc__
        if doc:
            doc = doc.strip()

        body = None
        if hasattr(func, 'sample_body'):
            body = func.sample_body

        response = None
        if hasattr(func, 'sample_response'):
            response = func.sample_response

        endpoints.append(
            Endpoint(
                method,
                url,
                section,
                doc,
                body,
                response
            ))

    errors = []

    functions = inspect.getmembers(error_funcs, inspect.isfunction)
    for (name, func) in functions:
        if name in ['prepare_error', 'jsonify']:
            # ignore this functions
            continue
        sig = inspect.signature(func)

        actual_error = None
        if len(sig.parameters) > 0:
            actual_error = func('param')
        else:
            actual_error = func()

        response_as_str = actual_error.response[0].decode('utf-8')
        response_body = loads(response_as_str)

        e = {
            'response_code': actual_error.status_code,
            'error': response_body['error']
        }
        errors.append(e)

    endpoints = sorted(endpoints, key=lambda e: e.section)
    errors = sorted(errors, key=lambda e: e['error']['code'])

    return jsonify({
        'success': 1,
        'endpoints': [e.__dict__ for e in endpoints],
        'errors': errors,
    })
