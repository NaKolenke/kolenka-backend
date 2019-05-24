from flask import Blueprint, jsonify, request
from playhouse.flask_utils import PaginatedQuery
from src.model.models import Post, Tag
from src import errors


bp = Blueprint('tags', __name__, url_prefix='/tags/')


@bp.route("/", methods=['GET'])
def tags():
    query = Tag.get_tags()
    limit = max(1, min(int(request.args.get('limit')) or 20, 100))
    paginated_query = PaginatedQuery(query, paginate_by=limit)

    return jsonify({
        'success': 1,
        'tags': [t.to_json() for t in paginated_query.get_object_list()],
        'meta': {
            'page_count': paginated_query.get_page_count()
        }
    })


@bp.route("/<title>/", methods=['GET'])
def tag(title):
    tag = Tag.get_or_none(Tag.title == title)
    if tag is None:
        return errors.not_found()

    query = Post.get_public_posts_with_tag(tag)
    limit = max(1, min(int(request.args.get('limit')) or 20, 100))
    paginated_query = PaginatedQuery(query, paginate_by=limit)

    return jsonify({
        'success': 1,
        'posts': [p.to_json() for p in paginated_query.get_object_list()],
        'meta': {
            'page_count': paginated_query.get_page_count()
        }
    })


@bp.route("/suggestion/", methods=['POST'])
def suggestion():
    json = request.get_json()
    if 'title' not in json:
        return errors.wrong_payload('title')

    title = json['title']
    query = Tag.select().where(Tag.title.contains(title))

    return jsonify({
        'success': 1,
        'tags': [t.to_json() for t in query],
    })
