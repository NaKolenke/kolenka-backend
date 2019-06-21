from flask import Blueprint, jsonify, request
from src.auth import login_required, get_user_from_request
from src.model.models import Sticker, Content
from src import errors

bp = Blueprint('stickers', __name__, url_prefix='/stickers/')


@bp.route('/', methods=['GET'])
@login_required
def get():
    query = Sticker.select()

    return jsonify({
        'success': 1,
        'stickers': [item.to_json() for item in query]
    })


@bp.route('/', methods=['POST'])
@login_required
def post():
    user = get_user_from_request()

    if not user.is_admin:
        return errors.no_access()

    json = request.get_json()

    if 'name' not in json or 'file' not in json:
        return errors.wrong_payload('name', 'file')

    if len(json['name']) == 0:
        return errors.wrong_payload('name')

    sticker = Sticker.create(
        name=json['name'],
        file=Content.get_or_none(Content.id == json['file'])
    )

    return jsonify({
        'success': 1,
        'sticker': sticker.to_json()
    })
