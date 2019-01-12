from flask import request, jsonify

def make_error(message, code=200):
    response = jsonify({
        'success': 0,
        'error': message
    })
    response.status_code = code
    return response
