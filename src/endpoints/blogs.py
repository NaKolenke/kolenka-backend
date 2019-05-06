import datetime
from flask import Blueprint, jsonify, request
from playhouse.shortcuts import model_to_dict
from playhouse.flask_utils import PaginatedQuery
from src.auth import login_required, get_user_from_request
from src.model.models import User, Blog, BlogParticipiation, Content, \
    BlogInvite, Post
from src.utils import make_error


bp = Blueprint('blogs', __name__, url_prefix='/blogs/')


@bp.route("/", methods=['GET', 'POST'])
def blogs():
    if request.method == 'GET':
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
    elif request.method == 'POST':
        user = get_user_from_request()
        if user is None:
            return make_error(
                'You should be authorized to use this endpoint',
                401)

        blog = Blog.create(
            created_date=datetime.datetime.now(),
            updated_date=datetime.datetime.now(),
            creator=user,
        )

        BlogParticipiation.create(
            blog=blog,
            user=user,
            role=1)

        blog_dict = model_to_dict(blog, exclude=[User.password])

        return jsonify({
            'success': 1,
            'blog': blog_dict,
        })


@bp.route("/<url>/", methods=['GET', 'PUT', 'DELETE'])
def blog(url):
    blog = Blog.get_or_none(Blog.url == url)
    if blog is None:
        return make_error('There is no blog with this url', 404)

    if request.method == 'GET':
        blog_dict = model_to_dict(blog, exclude=[User.password])
        blog_dict['readers'] = Blog.get_readers_count(blog)
        return jsonify({
            'success': 1,
            'blog': blog_dict,
        })
    elif request.method == 'DELETE':
        user = get_user_from_request()
        if user is None:
            return make_error(
                'You should be authorized to use this endpoint',
                401)

        role = Blog.get_user_role(blog, user)
        if role != 1:
            return make_error(
                'You doesn\'t have rights to do this action',
                403)

        blog.delete_instance()

        return jsonify({
            'success': 1
        })
    elif request.method == 'PUT':
        user = get_user_from_request()
        if user is None:
            return make_error(
                'You should be authorized to use this endpoint',
                401)

        role = Blog.get_user_role(blog, user)
        if role != 1:
            return make_error(
                'You doesn\'t have rights to do this action',
                403)

        json = request.get_json()

        blog.title = json.get('title', blog.title)
        blog.description = json.get('description', blog.description)
        blog.url = json.get('url', blog.url)
        blog.blog_type = json.get('blog_type', blog.blog_type)
        if 'image' in json:
            blog.image = Content.get_or_none(Content.id == json['image'])

        blog.updated_date = datetime.datetime.now()

        blog.save()

        blog_dict = model_to_dict(blog, exclude=[User.password])
        return jsonify({
            'success': 1,
            'blog': blog_dict
        })


@bp.route("/<url>/posts/")
def posts(url):
    blog = Blog.get_or_none(Blog.url == url)
    if blog is None:
        return make_error('There is no blog with this url', 404)

    posts = []

    query = Post.select().where(
        (Post.is_draft == False) &  # noqa: E712
        (Post.blog == blog)
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


@bp.route("/<url>/readers/")
def readers(url):
    blog = Blog.get_or_none(Blog.url == url)
    if blog is None:
        return make_error('There is no blog with this url', 404)

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
        return make_error('There is no blog with this url', 404)

    user = get_user_from_request()

    json = request.get_json()

    if 'invite' in json:
        invite = BlogInvite.get_or_none(BlogInvite.id == json['invite'])
        if invite is None:
            return make_error('There is no invite with this id', 404)

        if invite.user_to.id != user.id:
            return make_error('You can\'t accept this invite', 403)

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
            return make_error('There is no user with this id', 400)

        role = Blog.get_user_role(blog, user)

        if role is None:
            return make_error('You are not participiate in this blog', 400)

        role_to = json['role']
        roles = {
            'owner': 1,
            'writer': 2,
            'reader': 3
        }

        if role_to not in roles:
            return make_error('Wrong role specified', 400)

        role_to = roles[role_to]
        if role > role_to:
            return make_error('You doesn\'t have rights to do this action',
                              400)

        invite = BlogInvite.create(blog=blog, user_from=user, user_to=user_to,
                                   role=role_to)

        return jsonify({
            'success': 1,
            'invite': invite.id,
        })
