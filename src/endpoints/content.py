import os
import ntpath
import hashlib
import datetime
from flask import Blueprint, jsonify, request, current_app, send_file
from playhouse.flask_utils import PaginatedQuery
from src.auth import login_required, get_user_from_request
from src.model.models import Content
from src import errors


bp = Blueprint('content', __name__, url_prefix='/content/')

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/', methods=['POST'])
@login_required
def upload():
    '''Загрузить файл'''
    if 'file' not in request.files:
        return errors.content_no_file()

    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return errors.content_no_file()

    if uploaded_file and allowed_file(uploaded_file.filename):
        user = get_user_from_request()

        name = hashlib.md5(uploaded_file.read()).hexdigest()
        uploaded_file.seek(0)

        _, ext = ntpath.splitext(uploaded_file.filename)

        today = datetime.date.today()

        filename = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            str(user.id) + '/' +
            str(today.year) + '/' +
            str(today.month) + '/')

        os.makedirs(filename, exist_ok=True)

        new_path = filename + name + ext

        uploaded_file.save(new_path)

        content = Content.create(user=user.id, path=os.path.abspath(new_path))

        return jsonify({
            'success': 1,
            'file': content.to_json()
        })


@bp.route('/owned/', methods=['GET'])
@login_required
def get_owned():
    query = Content.get_user_files(get_user_from_request())
    limit = max(1, min(int(request.args.get('limit') or 20), 100))
    paginated = PaginatedQuery(query, paginate_by=limit)

    return jsonify({
        'success': 1,
        'files': [p.to_json() for p in paginated.get_object_list()],
        'meta': {
            'page_count': paginated.get_page_count()
        }
    })


@bp.route('/<id>/', methods=['GET'])
def get(id):
    '''Получить файл по id'''
    content = Content.get_or_none(Content.id == id)
    if content is not None:
        return send_file(content.path)
    else:
        return errors.not_found()
