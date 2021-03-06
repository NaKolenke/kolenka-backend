import datetime

from flask import Blueprint, jsonify, request
from playhouse.flask_utils import PaginatedQuery

from src import errors
from src.auth import get_user_from_request, login_required
from src.model.models import (
    Blog,
    BlogInvite,
    BlogParticipiation,
    Content,
    Notification,
    Post,
    User,
    Vote,
)
from src.utils import doc_sample, sanitize

bp = Blueprint("blogs", __name__, url_prefix="/blogs/")


@bp.route("/", methods=["GET"])
def get_blogs():
    """Получить список публичных блогов"""
    query = Blog.get_public_blogs()
    limit = max(1, min(int(request.args.get("limit") or 20), 100))
    paginated_query = PaginatedQuery(query, paginate_by=limit)

    blogs = [b.to_json() for b in paginated_query.get_object_list()]
    blogs = [Vote.add_votes_info(b, 2, get_user_from_request()) for b in blogs]

    return jsonify(
        {
            "success": 1,
            "blogs": blogs,
            "meta": {"page_count": paginated_query.get_page_count()},
        }
    )


@bp.route("/", methods=["POST"])
@login_required
@doc_sample(
    body={
        "title": "some title",
        "description": "some description",
        "url": "url",
        "blog_type": "int, 1 - for open, 2 - private",
        "image": "content id",
    }
)
def create_blog():
    """Создать блог"""
    user = get_user_from_request()

    url = request.get_json()["url"]
    if Blog.get_or_none(Blog.url == url) is not None:
        return errors.blog_url_already_taken()

    blog = Blog.create(
        created_date=datetime.datetime.now(),
        updated_date=datetime.datetime.now(),
        creator=user,
    )

    BlogParticipiation.create(blog=blog, user=user, role=1)

    fill_blog_from_json(blog, request.get_json())
    blog.save()

    return jsonify({"success": 1, "blog": blog.to_json()})


@bp.route("/<url>/", methods=["GET"])
def get_single_blog(url):
    """Получить блог по указанному url"""
    blog = Blog.get_or_none(Blog.url == url)
    if blog is None:
        return errors.not_found()

    user = get_user_from_request()
    has_access = Blog.has_access(blog, user)

    if not has_access:
        return errors.no_access()

    blog_dict = blog.to_json()
    blog_dict = Vote.add_votes_info(blog_dict, 2, user)
    return jsonify({"success": 1, "blog": blog_dict})


@bp.route("/<url>/", methods=["PUT"])
@login_required
def edit_blog(url):
    """Изменить блог"""
    blog = Blog.get_or_none(Blog.url == url)
    if blog is None:
        return errors.not_found()

    user = get_user_from_request()

    role = Blog.get_user_role(blog, user)
    if role != 1:
        return errors.no_access()

    fill_blog_from_json(blog, request.get_json())

    if not validate_url(blog):
        return errors.blog_url_already_taken()

    blog.save()

    return jsonify({"success": 1, "blog": blog.to_json()})


@bp.route("/<url>/", methods=["DELETE"])
@login_required
def delete_blog(url):
    """Удалить блог"""
    blog = Blog.get_or_none(Blog.url == url)
    if blog is None:
        return errors.not_found()

    user = get_user_from_request()

    role = Blog.get_user_role(blog, user)
    if role != 1:
        return errors.no_access()

    blog.delete_instance()

    return jsonify({"success": 1})


@bp.route("/<url>/posts/")
def posts(url):
    """Получить список постов для блога"""
    blog = Blog.get_or_none(Blog.url == url)
    if blog is None:
        return errors.not_found()

    user = get_user_from_request()
    has_access = Blog.has_access(blog, user)
    if not has_access:
        return errors.no_access()

    query = Post.get_posts_for_blog(blog)
    limit = max(1, min(int(request.args.get("limit") or 20), 100))
    paginated_query = PaginatedQuery(query, paginate_by=limit)

    posts = [p.to_json() for p in paginated_query.get_object_list()]
    posts = [Vote.add_votes_info(p, 3, user) for p in posts]

    return jsonify(
        {
            "success": 1,
            "posts": posts,
            "meta": {"page_count": paginated_query.get_page_count()},
        }
    )


@bp.route("/<url>/readers/")
def readers(url):
    """Получить список читателей блога"""
    blog = Blog.get_or_none(Blog.url == url)
    if blog is None:
        return errors.not_foun
    user = get_user_from_request()
    has_access = Blog.has_access(blog, user)
    if not has_access:
        return errors.no_access()

    query = Blog.get_readers(blog)
    limit = max(1, min(int(request.args.get("limit") or 20), 100))
    paginated_query = PaginatedQuery(query, paginate_by=limit)

    return jsonify(
        {
            "success": 1,
            "readers": [u.to_json() for u in paginated_query.get_object_list()],
            "meta": {"page_count": paginated_query.get_page_count()},
        }
    )


@bp.route("/<url>/invite/", methods=["POST"])
@login_required
def invites(url):
    """Пригласить пользователя или принять инвайт"""
    blog = Blog.get_or_none(Blog.url == url)
    if blog is None:
        return errors.not_found()

    user = get_user_from_request()

    json = request.get_json()

    if "invite" in json:
        invite = BlogInvite.get_or_none(BlogInvite.id == json["invite"])
        if invite is None:
            return errors.invite_not_found()

        if invite.user_to.id != user.id:
            return errors.no_access()

        invite.is_accepted = True
        invite.save()

        BlogParticipiation.create(blog=invite.blog, user=user, role=invite.role)

        return jsonify({"success": 1})
    elif "user" in json and "role" in json:
        user_to = User.get_or_none(User.id == json["user"])
        if user_to is None:
            return errors.not_found()

        role = Blog.get_user_role(blog, user)

        if role is None:
            return errors.no_access()

        role_to = json["role"]
        roles = {"owner": 1, "writer": 2, "reader": 3}

        if role_to not in roles:
            return errors.invite_wrong_role()

        role_to = roles[role_to]
        if role > role_to:
            return errors.no_access()

        invite = BlogInvite.create(
            blog=blog, user_from=user, user_to=user_to, role=role_to
        )

        Notification.create(
            user=user,
            created_date=datetime.datetime.now(),
            text='Вас пригласили в блог "{0}"'.format(blog.title),
            object_type="invite",
            object_id=invite.id,
        )

        return jsonify({"success": 1, "invite": invite.id})


@bp.route("/<url>/join/", methods=["GET", "POST"])
@login_required
def join(url):
    """Присоеденится к блогу. Работает только с открытми блогами"""
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

    return jsonify({"success": 1})


def fill_blog_from_json(blog, json):
    if json is not None:
        blog.title = json.get("title", blog.title)
        blog.description = sanitize(json.get("description", blog.description))
        blog.url = json.get("url", blog.url)
        blog.blog_type = json.get("blog_type", blog.blog_type)
        if "image" in json:
            blog.image = Content.get_or_none(Content.id == json["image"])

    blog.updated_date = datetime.datetime.now()


def validate_url(blog):
    new_url = blog.url
    print(new_url)
    blogs_with_url = Blog.select().where(Blog.url == new_url)
    for b in blogs_with_url:
        if b.url == new_url and b.id != blog.id:
            return False

    return True
