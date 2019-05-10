from flask import Blueprint, jsonify, request
from peewee import fn
from playhouse.shortcuts import model_to_dict
from playhouse.flask_utils import PaginatedQuery
from src.model.models import Post, Tag, TagMark, User, Blog
from src.utils import make_error


bp = Blueprint('tags', __name__, url_prefix='/tags/')


@bp.route("/", methods=['GET'])
def tags():
    tags = []

    query = (Tag
        .select(Tag.title, Tag.id, fn.COUNT(TagMark.id).alias('count'))
        .join(TagMark)
        .group_by(Tag.title)
        .order_by(Tag.created_date.desc()))

    paginated_query = PaginatedQuery(query, paginate_by=20)
    for t in paginated_query.get_object_list():
        tag_dict = model_to_dict(t, exclude=[])
        tags.append(tag_dict)
    return jsonify({
        'success': 1,
        'tags': tags,
        'meta': {
            'page_count': paginated_query.get_page_count()
        }
    })


@bp.route("/<title>/", methods=['GET'])
def tag(title):
    tag = Tag.get_or_none(Tag.title == title)
    if tag is None:
        return make_error('There is no tag with this url', 404)

    posts = []

    query = Post\
        .select()\
        .join(TagMark)\
        .switch(Post)\
        .join(Blog)\
        .where(
            (Post.is_draft == False) &  # noqa: E712
            (TagMark.tag == tag) &
            (Blog.blog_type != 3)
        ).order_by(Post.created_date.desc())

    paginated_query = PaginatedQuery(query, paginate_by=20)
    for p in paginated_query.get_object_list():
        post_dict = model_to_dict(p, exclude=[User.password])
        posts.append(post_dict)

    return jsonify({
        'success': 1,
        'posts': posts,
        'meta': {
            'page_count': paginated_query.get_page_count()
        }
    })


@bp.route("/suggestion/", methods=['POST'])
def suggestion():
    json = request.get_json()
    if 'title' not in json:
        return make_error('Provide title in response body', 400)

    title = json['title']

    query = Tag.select().where(Tag.title.contains(title))

    tags = []

    for t in query:
        tag_dict = model_to_dict(t, exclude=[])
        tags.append(tag_dict)

    return jsonify({
        'success': 1,
        'tags': tags,
    })
