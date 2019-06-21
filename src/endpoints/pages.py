import datetime
from flask import Blueprint, jsonify, request
from playhouse.flask_utils import PaginatedQuery
from src.auth import get_user_from_request, login_required
from src.model.models import Post, Blog, Comment
from src import errors

bp = Blueprint('pages', __name__, url_prefix='/pages/')

