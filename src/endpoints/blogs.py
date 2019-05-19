import datetime
from flask import Blueprint, jsonify, request
from playhouse.shortcuts import model_to_dict
from playhouse.flask_utils import PaginatedQuery
from src.auth import login_required, get_user_from_request
from src.endpoints import posts as posts_endpoint
from src.model.models import User, Blog, BlogParticipiation, Content, \
    BlogInvite, Post
from src import errors


bp = Blueprint('blogs', __name__, url_prefix='/blogs/')


@bp.route("/", methods=['GET'])
def get_blogs():
    blogs = []
    query = Blog.select().where(Blog.blog_type != 3)
    paginated_query = PaginatedQuery(query, paginate_by=20)

    for b in paginated_query.get_object_list():
        blog_dict = model_to_dict(b, exclude=[User.password])
        blog_dict['readers'] = Blog.get_readers_count(b)
        blogs.append(blog_dict)

    return jsonify({
        'success': 1,
        'blogs': blogs,
        'meta': {
            'page_count': paginated_query.get_page_count()
        }
    })


@bp.route("/", methods=['POST'])
def create_blog():
    user = get_user_from_request()
    if user is None:
        return errors.not_authorized()

    blog = Blog.create(
        created_date=datetime.datetime.now(),
        updated_date=datetime.datetime.now(),
        creator=user,
    )

    BlogParticipiation.create(
        blog=blog,
        user=user,
        role=1)

    fill_blog_from_json(blog, request.get_json())
    blog.save()

    blog_dict = model_to_dict(blog, exclude=[User.password])

    return jsonify({
        'success': 1,
        'blog': blog_dict,
    })


@bp.route("/<url>/", methods=['GET'])
def get_single_blog(url):
    blog = Blog.get_or_none(Blog.url == url)
    if blog is None:
        return errors.not_found()

    user = get_user_from_request()
    has_access = Blog.has_access(blog, user)

    if not has_access:
        return errors.no_access()

    blog_dict = model_to_dict(blog, exclude=[User.password])
    blog_dict['readers'] = Blog.get_readers_count(blog)
    return jsonify({
        'success': 1,
        'blog': blog_dict,
    })


@bp.route("/<url>/", methods=['PUT'])
def edit_blog(url):
    blog = Blog.get_or_none(Blog.url == url)
    if blog is None:
        return errors.not_found()

    user = get_user_from_request()
    if user is None:
        return errors.not_authorized()

    role = Blog.get_user_role(blog, user)
    if role != 1:
        return errors.no_access()

    fill_blog_from_json(blog, request.get_json())
    blog.save()

    blog_dict = model_to_dict(blog, exclude=[User.password])
    return jsonify({
        'success': 1,
        'blog': blog_dict
    })


@bp.route("/<url>/", methods=['DELETE'])
def delete_blog(url):
    blog = Blog.get_or_none(Blog.url == url)
    if blog is None:
        return errors.not_found()

    user = get_user_from_request()
    if user is None:
        return errors.not_authorized()

    role = Blog.get_user_role(blog, user)
    if role != 1:
        return errors.no_access()

    blog.delete_instance()

    return jsonify({
        'success': 1
    })


@bp.route("/<url>/posts/")
def posts(url):
    blog = Blog.get_or_none(Blog.url == url)
    if blog is None:
        return errors.not_found()
    user = get_user_from_request()
    has_access = Blog.has_access(blog, user)
    if not has_access:
        return errors.no_access()

    posts = []

    query = Post.select().where(
        (Post.is_draft == False) &  # noqa: E712
        (Post.blog == blog)
    ).order_by(Post.created_date.desc())

    paginated_query = PaginatedQuery(query, paginate_by=20)
    for p in paginated_query.get_object_list():
        post_dict = posts_endpoint.prepare_post_to_response(p)
        posts.append(post_dict)
    return jsonify({
        'success': 1,
        'posts': posts,
        'meta': {
            'page_count': paginated_query.get_page_count()
        }
    })


@bp.route("/<url>/readers/")
def readers(url):
    blog = Blog.get_or_none(Blog.url == url)
    if blog is None:
        return errors.not_foun
    user = get_user_from_request()
    has_access = Blog.has_access(blog, user)
    if not has_access:
        return errors.no_access()

    readers = []

    query = Blog.get_readers(blog)
    paginated_query = PaginatedQuery(query, paginate_by=20)
    for u in paginated_query.get_object_list():
        readers.append(
            model_to_dict(
                u,
                exclude=[User.password, User.birthday, User.about]))

    return jsonify({
        'success': 1,
        'readers': readers,
        'meta': {
            'page_count': paginated_query.get_page_count()
        }
    })


@bp.route("/<url>/invite/", methods=['POST'])
@login_required
def invites(url):
    blog = Blog.get_or_none(Blog.url == url)
    if blog is None:
        return errors.not_found()

    user = get_user_from_request()

    json = request.get_json()

    if 'invite' in json:
        invite = BlogInvite.get_or_none(BlogInvite.id == json['invite'])
        if invite is None:
            return errors.invite_not_found()

        if invite.user_to.id != user.id:
            return errors.no_access()

        invite.is_accepted = True
        invite.save()

        BlogParticipiation.create(blog=invite.blog, user=user,
                                  role=invite.role)

        return jsonify({
            'success': 1
        })
    elif 'user' in json and 'role' in json:
        user_to = User.get_or_none(User.id == json['user'])
        if user_to is None:
            return errors.not_found()

        role = Blog.get_user_role(blog, user)

        if role is None:
            return errors.no_access()

        role_to = json['role']
        roles = {
            'owner': 1,
            'writer': 2,
            'reader': 3
        }

        if role_to not in roles:
            return errors.invite_wrong_role()

        role_to = roles[role_to]
        if role > role_to:
            return errors.no_access()

        invite = BlogInvite.create(blog=blog, user_from=user, user_to=user_to,
                                   role=role_to)

        return jsonify({
            'success': 1,
            'invite': invite.id,
        })


@bp.route("/<url>/join/", methods=['GET', 'POST'])
@login_required
def join(url):
    blog = Blog.get_or_none(Blog.url == url)
    if blog is None:
        return errors.not_found()
    if blog.blog_type != 1:
        return errors.no_access()

    user = get_user_from_request()
    if user is None:
        return errors.not_authorized()
    if BlogParticipiation.get_or_none(blog=blog, user=user) is None:
        BlogParticipiation.create(blog=blog, user=user, role=3)

    return jsonify({
            'success': 1
        })


def fill_blog_from_json(blog, json):
    if json is not None:
        blog.title = json.get('title', blog.title)
        blog.description = json.get('description', blog.description)
        blog.url = json.get('url', blog.url)
        blog.blog_type = json.get('blog_type', blog.blog_type)
        if 'image' in json:
            blog.image = Content.get_or_none(Content.id == json['image'])

    blog.updated_date = datetime.datetime.now()
