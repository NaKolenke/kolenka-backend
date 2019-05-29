import datetime
from flask import Blueprint, jsonify, request
from playhouse.flask_utils import PaginatedQuery
from src.auth import login_required, get_user_from_request
from src.model.models import Notification
from src import errors


bp = Blueprint('notifications', __name__, url_prefix='/notifications/')


@bp.route('/', methods=['GET'])
@login_required
def get():
    query = Notification.get_user_notifications(get_user_from_request())
    limit = max(1, min(int(request.args.get('limit') or 20), 100))
    paginated = PaginatedQuery(query, paginate_by=limit)

    return jsonify({
        'success': 1,
        'notifications': [p.to_json() for p in paginated.get_object_list()],
        'meta': {
            'page_count': paginated.get_page_count()
        }
    })


@bp.route('/', methods=['PUT'])
@login_required
def mark_as_read():
    user = get_user_from_request()
    json = request.get_json()
    if 'ids' in json:
        for i in json['ids']:
            Notification.mark_notification_as_readed(user, i)
    else:
        return errors.wrong_payload('ids')
    return jsonify({
        'success': 1,
    })


@bp.route('/test', methods=['GET'])
@login_required
def test_notification():
    user = get_user_from_request()
    n = Notification.create(
        user=user,
        created_date=datetime.datetime.now(),
        text='Это тестовое уведомление')

    return jsonify({
        'success': 1,
        'notification': n.to_json()
    })
