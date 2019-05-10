import datetime
from flask import Blueprint, jsonify, request
from playhouse.shortcuts import model_to_dict
from playhouse.flask_utils import PaginatedQuery
from src.auth import get_user_from_request
from src.model.models import User, Post, Blog, Comment
from src.utils import make_error


bp = Blueprint('posts', __name__, url_prefix='/posts/')


@bp.route("/", methods=['GET', 'POST'])
def posts():
    if request.method == 'GET':
        posts = []

        query = Post.select().where(
            # (Post.is_on_main) &
            (Post.is_draft == False)  # noqa: E712
        ).order_by(Post.created_date.desc())

        paginated_query = PaginatedQuery(query, paginate_by=20)
        for p in paginated_query.get_object_list():
            post_dict = prepare_post_to_response(p)
            posts.append(post_dict)
        return jsonify({
            'success': 1,
            'posts': posts,
            'meta': {
                'page_count': paginated_query.get_page_count()
            }
        })
    elif request.method == 'POST':
        user = get_user_from_request()
        if user is None:
            return make_error(
                'You should be authorized to use this endpoint',
                401)

        post = Post.create(
            created_date=datetime.datetime.now(),
            updated_date=datetime.datetime.now(),
            creator=user,
        )

        fill_post_from_json(post, request.get_json())
        post.save()

        post_dict = prepare_post_to_response(post)

        return jsonify({
            'success': 1,
            'post': post_dict,
        })


@bp.route("/<url>/", methods=['GET', 'PUT', 'DELETE'])
def post(url):
    post = Post.get_or_none(Post.url == url)
    if post is None:
        return make_error('There is no post with this url', 404)

    if request.method == 'GET':
        if post.is_draft:
            user = get_user_from_request()
            if user is None:
                return make_error(
                    'You doesn\'t have rights to do this action',
                    403)

            if post.creator != user:
                return make_error(
                    'You doesn\'t have rights to do this action',
                    403)

        post_dict = prepare_post_to_response(post)

        return jsonify({
            'success': 1,
            'post': post_dict,
        })
    elif request.method == 'DELETE':
        user = get_user_from_request()
        if user is None:
            return make_error(
                'You should be authorized to use this endpoint',
                401)

        if post.creator == user:
            post.delete_instance()

            return jsonify({
                'success': 1
            })

        if post.blog is None:
            return make_error(
                'You doesn\'t have rights to do this action',
                403)

        role = Blog.get_user_role(post.blog, user)
        if role != 1:
            return make_error(
                'You doesn\'t have rights to do this action',
                403)

        post.delete_instance()

        return jsonify({
            'success': 1
        })
    elif request.method == 'PUT':
        user = get_user_from_request()
        if user is None:
            return make_error(
                'You should be authorized to use this endpoint',
                401)

        role = Blog.get_user_role(post.blog, user)
        if role != 1 or post.creator != user:
            return make_error(
                'You doesn\'t have rights to do this action',
                403)

        fill_post_from_json(post, request.get_json())

        post.save()

        post_dict = prepare_post_to_response(post)
        return jsonify({
            'success': 1,
            'post': post_dict
        })


@bp.route("/<url>/comments/", methods=['GET', 'POST'])
def comments(url):
    post = Post.get_or_none(Post.url == url)
    if post is None:
        return make_error('There is no post with this url', 404)
    if request.method == 'GET':
        if post.is_draft:
            user = get_user_from_request()
            if user is None:
                return make_error(
                    'You doesn\'t have rights to do this action',
                    403)

            if post.creator != user:
                return make_error(
                    'You doesn\'t have rights to do this action',
                    403)

        comments = []

        for c in Comment.select().where(Comment.post == post):
            comment_dict = model_to_dict(
                c,
                exclude=[User.password, Comment.post])
            comments.append(comment_dict)
        return jsonify({
            'success': 1,
            'comments': comments,
        })
    elif request.method == 'POST':
        user = get_user_from_request()
        if user is None:
            return make_error(
                'You should be authorized to use this endpoint',
                401)

        json = request.get_json()

        if 'text' in json:
            text = json.get('text')
        else:
            return make_error(
                'You should fill text field',
                400)

        parent = None
        level = 0
        if 'parent' in json:
            parent = Comment.get_or_none(Comment.id == json['parent'])
            if parent is not None:
                level = parent.level + 1

        comment = Comment.create(
            post=post,
            created_date=datetime.datetime.now(),
            updated_date=datetime.datetime.now(),
            creator=user,
            text=text,
            parent=parent,
            level=level
        )

        comment_dict = model_to_dict(
                comment,
                exclude=[User.password, Comment.post])

        return jsonify({
            'success': 1,
            'comment': comment_dict,
        })


def prepare_post_to_response(post):
    post_dict = model_to_dict(post, exclude=[User.password])
    post_dict['comments'] = Comment.get_comments_count_for_post(post)
    return post_dict


def fill_post_from_json(post, json):
    if json is not None:
        post.title = json.get('title', post.title)
        post.text = json.get('text', post.text)

        post.has_cut = '<cut>' in post.text
        post.cut_text = post.text.split('<cut>')[0]
        post.cut_name = json.get('cut_name', post.cut_name)

        post.is_draft = json.get('is_draft', post.is_draft)
        post.url = json.get('url', post.url)

        if 'blog' in json:
            post.blog = Blog.get_or_none(Blog.id == json['blog'])

    post.updated_date = datetime.datetime.now()
