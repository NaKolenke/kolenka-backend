import os
import ntpath
from flask import Blueprint, jsonify, request, current_app, send_file
from playhouse.shortcuts import model_to_dict
from werkzeug.utils import secure_filename
from src.auth import login_required, get_user_from_request
from src.model.models import Content
from src.utils import make_error


bp = Blueprint('content', __name__, url_prefix='/content/')

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/', methods=['POST'])
@login_required
def upload():
    if 'file' not in request.files:
        return make_error('No file part')

    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return make_error('No selected file')

    if uploaded_file and allowed_file(uploaded_file.filename):
        user = get_user_from_request()
        filename = user.login + ntpath.basename(uploaded_file.filename)
        filename = secure_filename(filename)
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        uploaded_file.save(path)
        content = Content.create(user=user.id, path=os.path.abspath(path))
        return jsonify({
            'success': 1,
            'file': model_to_dict(content, exclude=[Content.user])
        })

@bp.route('/<id>/', methods=['GET'])
def get(id):
    content = Content.get_or_none(Content.id == id)
    if content is not None:
        return send_file(content.path)
    else:
        return make_error('No file', 404)
