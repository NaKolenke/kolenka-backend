import datetime
from flask import Blueprint, jsonify, request
from playhouse.shortcuts import model_to_dict
from playhouse.flask_utils import PaginatedQuery
from src.auth import get_user_from_request
from src.model.models import User, Post, Blog, Comment
from src import errors


class BlogError:
    NoBlog = 1
    NoAccess = 2


bp = Blueprint('posts', __name__, url_prefix='/posts/')


@bp.route("/", methods=['GET'])
def get_posts():
    posts = []

    query = Post.select().join(Blog).where(
        # (Post.is_on_main) &
        (Post.is_draft == False) &  # noqa: E712
        (Blog.blog_type != 3)
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


@bp.route("/", methods=['POST'])
def create_post():
    user = get_user_from_request()
    if user is None:
        return errors.not_authorized()

    post = Post(
        created_date=datetime.datetime.now(),
        updated_date=datetime.datetime.now(),
        creator=user,
    )

    json = request.get_json()
    fill_post_from_json(post, json)
    error = set_blog(post, json, user)
    if error is not None:
        error_response = {
            BlogError.NoBlog: errors.not_found(),
            BlogError.NoAccess: errors.no_access()
        }[error]
        return error_response

    post.save()

    post_dict = prepare_post_to_response(post)

    return jsonify({
        'success': 1,
        'post': post_dict,
    })


@bp.route("/<url>/", methods=['GET'])
def get_post(url):
    post = Post.get_or_none(Post.url == url)
    if post is None:
        return errors.not_found()

    if post.is_draft:
        user = get_user_from_request()
        if user is None:
            return errors.no_access()

        if post.creator != user:
            return errors.no_access()

    user = get_user_from_request()
    has_access = Blog.has_access(post.blog, user)
    if not has_access:
        return errors.no_access()

    post_dict = prepare_post_to_response(post)

    return jsonify({
        'success': 1,
        'post': post_dict,
    })


@bp.route("/<url>/", methods=['PUT'])
def edit_post(url):
    post = Post.get_or_none(Post.url == url)
    if post is None:
        return errors.not_found()

    user = get_user_from_request()
    if user is None:
        return errors.not_authorized()

    role = Blog.get_user_role(post.blog, user)
    if role != 1 or post.creator != user:
        return errors.no_access()

    json = request.get_json()
    fill_post_from_json(post, json)
    error = set_blog(post, json, user)
    if error is not None:
        error_response = {
            BlogError.NoBlog: errors.not_found(),
            BlogError.NoAccess: errors.no_access()
        }[error]
        return error_response

    post.save()

    post_dict = prepare_post_to_response(post)
    return jsonify({
        'success': 1,
        'post': post_dict
    })


@bp.route("/<url>/", methods=['DELETE'])
def delete_post(url):
    post = Post.get_or_none(Post.url == url)
    if post is None:
        return errors.not_found()

    user = get_user_from_request()
    if user is None:
        return errors.not_authorized()

    if post.creator == user:
        post.delete_instance()

        return jsonify({
            'success': 1
        })

    if post.blog is None:
        return errors.no_access()

    role = Blog.get_user_role(post.blog, user)
    if role != 1:
        return errors.no_access()

    post.delete_instance()

    return jsonify({
        'success': 1
    })


@bp.route("/<url>/comments/", methods=['GET', 'POST'])
def comments(url):
    post = Post.get_or_none(Post.url == url)
    if post is None:
        return errors.not_found()
    if request.method == 'GET':
        if post.is_draft:
            user = get_user_from_request()
            if user is None:
                return errors.no_access()

            if post.creator != user:
                return errors.no_access()

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
            return errors.not_authorized()

        json = request.get_json()

        if 'text' in json:
            text = json.get('text')
        else:
            return errors.wrong_payload('text')

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

    post.updated_date = datetime.datetime.now()


def set_blog(post, json, user):
    if json is not None:
        if 'blog' in json:
            blog = Blog.get_or_none(Blog.id == json['blog'])
            if blog is not None:
                role = Blog.get_user_role(blog, user)
                if role is None:
                    return BlogError.NoAccess
                if blog.blog_type == 1:
                    post.blog = blog
                elif blog.blog_type == 2 or blog.blog_type == 3:
                    if role < 3:
                        post.blog = blog
                    else:
                        return BlogError.NoAccess
            else:
                return BlogError.NoBlog
