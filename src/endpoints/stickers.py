from flask import Blueprint, jsonify, request
from src.auth import login_required, get_user_from_request
from src.model.models import Sticker, Content
import src.endpoints.content as content_bp
from src import errors

bp = Blueprint('stickers', __name__, url_prefix='/stickers/')


@bp.route('/', methods=['GET'])
def get():
    query = Sticker.select()

    return jsonify({
        'success': 1,
        'stickers': [item.to_json() for item in query]
    })


@bp.route('/<name>/', methods=['GET'])
def get_sticker(name):
    sticker = Sticker.get_or_none(Sticker.name == name)
    if sticker is None:
        return errors.not_found()

    return content_bp.get(sticker.file.id)


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

    content = Content.get_or_none(Content.id == json['file'])
    if content:
        if not content.is_image:
            return errors.sticker_is_not_image()
        elif not content.is_small_image:
            return errors.sticker_too_large()

    sticker = Sticker.create(
        name=json['name'],
        file=content
    )

    return jsonify({
        'success': 1,
        'sticker': sticker.to_json()
    })
