from flask import Blueprint, jsonify, request
from playhouse.flask_utils import PaginatedQuery
from src.model.models import Post, Tag
from src import errors
from src.utils import doc_sample


bp = Blueprint('tags', __name__, url_prefix='/tags/')


@bp.route("/", methods=['GET'])
def tags():
    '''Получить список тегов, отсортированный по популярности'''
    query = Tag.get_tags()
    limit = max(1, min(int(request.args.get('limit') or 20), 100))
    paginated_query = PaginatedQuery(query, paginate_by=limit)

    return jsonify({
        'success': 1,
        'tags': [t.to_json() for t in paginated_query.get_object_list()],
        'meta': {
            'page_count': paginated_query.get_page_count()
        }
    })


@bp.route("/<title>/", methods=['GET'])
@doc_sample(body={})
def tag(title):
    '''
    Получить посты с указанным тегом
    '''
    tag = Tag.get_or_none(Tag.title == title)
    if tag is None:
        return errors.not_found()

    query = Post.get_public_posts_with_tag(tag)
    limit = max(1, min(int(request.args.get('limit') or 20), 100))
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
    '''Получить список предлагаемых тегов для автодополнения'''
    json = request.get_json()
    if 'title' not in json:
        return errors.wrong_payload('title')

    title = json['title']
    query = Tag.select().where(Tag.title.contains(title))

    return jsonify({
        'success': 1,
        'tags': [t.to_json() for t in query],
    })
