from flask import Blueprint, jsonify, request
from peewee import fn
from playhouse.shortcuts import model_to_dict
from playhouse.flask_utils import PaginatedQuery
from src.model.models import Post, Tag, TagMark, User, Blog
from src import errors


bp = Blueprint('tags', __name__, url_prefix='/tags/')


@bp.route("/", methods=['GET'])
def tags():
    tags = []

    ntags = fn.COUNT(TagMark.id)
    query = (Tag
             .select(Tag, ntags.alias('count'))
             .join(TagMark)
             .group_by(Tag.id)
             .order_by(ntags.desc()))

    paginated_query = PaginatedQuery(query, paginate_by=20)
    for t in paginated_query.get_object_list():
        tag_dict = model_to_dict(t, exclude=[])
        tag_dict['count'] = t.count
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
        return errors.not_found()

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
        return errors.wrong_payload('title')

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
