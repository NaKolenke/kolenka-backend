from datetime import datetime, date, timezone
from flask import request, jsonify
from flask.json import JSONEncoder

def make_error(message, code=200):
    response = jsonify({
        'success': 0,
        'error': message
    })
    response.status_code = code
    return response

def send_error(error, code=200):
    response = jsonify({
        'success': 0,
        'error': error.__dict__
    })
    response.status_code = code
    return response


class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                millis = int(obj.replace(tzinfo=timezone.utc).timestamp())
                return millis
            if isinstance(obj, date):
                millis = int(obj.replace(tzinfo=timezone.utc).timestamp())
                return millis
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)
