import datetime
import re

from flask import Blueprint, jsonify, request
from playhouse.flask_utils import PaginatedQuery

from src import errors
from src.auth import get_user_from_request, login_required
from src.endpoints._comments import _add_comment, _edit_comment, _get_comments
from src.model.models import (
    Blog,
    Comment,
    JamEntry,
    JamEntryPost,
    Notification,
    Post,
    Tag,
    TagMark,
    Vote,
)
from src.utils import sanitize


class BlogError:
    NoBlog = 1
    NoAccess = 2


bp = Blueprint("posts", __name__, url_prefix="/posts/")


@bp.route("/", methods=["GET"])
def get_posts():
    """Получить список публичных постов"""
    query = Post.get_public_posts()
    limit = max(1, min(int(request.args.get("limit") or 20), 100))
    paginated_query = PaginatedQuery(query, paginate_by=limit)

    posts = [p.to_json() for p in paginated_query.get_object_list()]
    posts = [Vote.add_votes_info(p, 3, get_user_from_request()) for p in posts]

    return jsonify(
        {
            "success": 1,
            "posts": posts,
            "meta": {"page_count": paginated_query.get_page_count()},
        }
    )


@bp.route("/", methods=["POST"])
@login_required
def create_post():
    """Создать пост"""
    user = get_user_from_request()

    post = Post(
        created_date=datetime.datetime.now(),
        updated_date=datetime.datetime.now(),
        creator=user,
    )

    json = request.get_json()

    url = json["url"]
    if Post.get_or_none(Post.url == url) is not None:
        return errors.post_url_already_taken()

    error = set_blog(post, json, user)
    if error is not None:
        error_response = {
            BlogError.NoBlog: errors.blog_not_found(),
            BlogError.NoAccess: errors.blog_no_access(),
        }[error]
        return error_response

    fill_post_from_json(post, json)

    post.save()

    set_tags_for_post(post, json)

    manage_jam_entries(post, json)

    return jsonify({"success": 1, "post": post.to_json()})


@bp.route("/<url>/", methods=["GET"])
def get_post(url):
    """Получить пост по url"""
    post = Post.get_or_none(Post.url == url)
    return _get_post(post)


@bp.route("/by-id/<id>/", methods=["GET"])
def get_post_by_id(id):
    """Получить пост по id"""
    post = Post.get_or_none(Post.id == id)
    return _get_post(post)


def _get_post(post):
    if post is None:
        return errors.not_found()

    if post.is_draft:
        user = get_user_from_request()
        if user is None:
            return errors.no_access()

        if post.creator != user:
            return errors.no_access()

    user = get_user_from_request()

    if post.blog is not None:
        # workaround, delete later. Sometime in the past you can save post
        # without blog, so this check will fail.
        has_access = Blog.has_access(post.blog, user)
        if not has_access:
            return errors.no_access()

    post_dict = post.to_json()
    post_dict = Vote.add_votes_info(post_dict, 3, user)

    entries = JamEntry.get_entries_for_post(post)
    post_dict["jam_entries"] = [e.to_json() for e in entries]

    return jsonify({"success": 1, "post": post_dict})


@bp.route("/<url>/", methods=["PUT"])
@login_required
def edit_post(url):
    """Изменить пост"""
    post = Post.get_or_none(Post.url == url)
    return _edit_post(post)


@bp.route("/by-id/<id>/", methods=["PUT"])
@login_required
def edit_post_by_id(id):
    """Изменить пост"""
    post = Post.get_or_none(Post.id == id)
    return _edit_post(post)


def _edit_post(post):
    if post is None:
        return errors.not_found()

    user = get_user_from_request()

    role = Blog.get_user_role(post.blog, user)

    if post.creator == user or role == 1 or user.is_admin:
        json = request.get_json()

        error = set_blog(post, json, user)
        if error is not None:
            error_response = {
                BlogError.NoBlog: errors.blog_not_found(),
                BlogError.NoAccess: errors.blog_no_access(),
            }[error]
            return error_response

        fill_post_from_json(post, json)

        if not validate_url(post):
            return errors.post_url_already_taken()

        post.save()

        set_tags_for_post(post, json)

        manage_jam_entries(post, json)

        return jsonify({"success": 1, "post": post.to_json()})
    else:
        return errors.no_access()


@bp.route("/<url>/", methods=["DELETE"])
@login_required
def delete_post(url):
    """Удалить пост"""
    post = Post.get_or_none(Post.url == url)
    return _delete_post(post)


@bp.route("/by-id/<id>/", methods=["DELETE"])
@login_required
def delete_post_by_id(id):
    """Удалить пост"""
    post = Post.get_or_none(Post.id == id)
    return _delete_post(post)


def _delete_post(post):
    if post is None:
        return errors.not_found()

    user = get_user_from_request()

    if post.creator == user or user.is_admin:
        Comment.delete().where(
            (Comment.object_type == "post") & (Comment.object_id == post.id)
        ).execute()
        TagMark.delete().where(TagMark.post == post).execute()
        post.delete_instance()

        return jsonify({"success": 1})

    if post.blog is None:
        return errors.no_access()

    role = Blog.get_user_role(post.blog, user)
    # only blog owner can delete posts
    if role != 1:
        return errors.no_access()

    Comment.delete().where(
        (Comment.object_type == "post") & (Comment.object_id == post.id)
    ).execute()
    TagMark.delete().where(TagMark.post == post).execute()
    post.delete_instance()

    return jsonify({"success": 1})


@login_required
@bp.route("/<url>/comments/", methods=["GET", "POST"])
def comments(url):
    """Получить список комментариев для поста или добавить новый комментарий"""
    post = Post.get_or_none(Post.url == url)
    if post is None:
        return errors.not_found()

    if request.method == "GET":
        user = get_user_from_request()
        if post.is_draft:

            if user is None:
                return errors.no_access()

            if post.creator != user:
                return errors.no_access()
        return _get_comments("post", post.id, user)
    elif request.method == "POST":
        user = get_user_from_request()
        if user is None:
            return errors.not_authorized()

        json = request.get_json()

        if "text" in json:
            text = sanitize(json.get("text"))
        else:
            return errors.wrong_payload("text")

        parent_id = None
        if "parent" in json:
            parent_id = json["parent"]
        parent = None
        if parent_id:
            parent = Comment.get_or_none(Comment.id == parent_id)

        comment = _add_comment("post", post.id, user, text, parent_id)

        if user.id != post.creator.id:
            t = "Пользователь {0} оставил комментарий к вашему посту {1}: {2}"
            notification_text = t.format(user.visible_name, post.title, text)

            Notification.create(
                user=post.creator,
                created_date=datetime.datetime.now(),
                text=notification_text,
                object_type="comment",
                object_id=comment.id,
            )

        if parent is not None:
            if user.id != parent.creator.id:
                t = "Пользователь {0} ответил на ваш комментарий {1}: {2}"
                notification_text = t.format(user.visible_name, parent.text, text)

                Notification.create(
                    user=parent.creator,
                    created_date=datetime.datetime.now(),
                    text=notification_text,
                    object_type="comment",
                    object_id=comment.id,
                )

        return jsonify({"success": 1, "comment": comment.to_json()})


@login_required
@bp.route("/<url>/comments/<comment_id>/", methods=["PUT"])
def edit_comment(url, comment_id):
    """Редактировать комментарий"""
    post = Post.get_or_none(Post.url == url)
    if post is None:
        return errors.not_found()

    user = get_user_from_request()
    if user is None:
        return errors.not_authorized()

    json = request.get_json()

    text = None
    if "text" in json:
        text = sanitize(json.get("text"))
    else:
        return errors.wrong_payload("text")

    comment = _edit_comment(comment_id, user, text)

    return jsonify({"success": 1, "comment": comment.to_json()})


def fill_post_from_json(post, json):
    if json is not None:
        post.title = json.get("title", post.title)
        post.text = sanitize(json.get("text", post.text))

        if post.text is not None:
            cut_info = process_cut(post.text)
            post.has_cut = cut_info["has_cut"]
            post.cut_text = cut_info["text_before_cut"]
            post.cut_name = cut_info["cut_name"]

        post.is_draft = json.get("is_draft", post.is_draft)
        post.url = json.get("url", post.url)

    post.updated_date = datetime.datetime.now()


def validate_url(post):
    new_url = post.url

    posts_with_url = Post.select().where(Post.url == new_url)
    for p in posts_with_url:
        if p.url == new_url and p.id != post.id:
            return False

    return True


def set_tags_for_post(post, json):
    if json is not None:
        tags = json.get("tags", [])
        TagMark.delete().where(TagMark.post == post).execute()
        for t in tags:
            tag = Tag.get_or_none(Tag.title == t)
            if tag is None:
                tag = Tag.create(title=t, created_date=datetime.datetime.now())
            TagMark.create(tag=tag, post=post)


def set_blog(post, json, user):
    if json is not None:
        if "blog" in json:
            blog = Blog.get_or_none(Blog.id == json["blog"])
            if blog is not None:
                # admin can save to any blog
                if user.is_admin:
                    post.blog = blog
                    return

                role = Blog.get_user_role(blog, user)

                # if user not in blog - then he can't save post here
                if role is None:
                    return BlogError.NoAccess
                # if blog is open - anyone can post here
                if blog.blog_type == 1:
                    post.blog = blog
                # if blog is closed or hidden - only writers and admins can
                # save posts here
                elif blog.blog_type == 2 or blog.blog_type == 3:
                    if role < 3:
                        post.blog = blog
                    else:
                        return BlogError.NoAccess
            else:
                return BlogError.NoBlog


def process_cut(post):
    has_simple_cut = "<cut>" in post or "<cut/>" in post
    has_named_cut = '<cut name="' in post

    cut_name = ""
    text_before_cut = post
    if has_simple_cut:
        text_before_cut = post[0 : post.find("<cut>")]
    elif has_named_cut:
        text_before_cut = post[0 : post.find("<cut ")]
        m = re.search(r'<cut name="([a-zA-Zа-яА-Я0-9 \-_,.!?\']*)">', post)
        print(m)
        cut_name = m.group(1)

    return {
        "has_cut": has_named_cut or has_simple_cut,
        "cut_name": cut_name if has_named_cut else "",
        "text_before_cut": text_before_cut,
    }


def manage_jam_entries(post, json):
    if json is not None:
        entries = json.get("jam_entries", [])
        JamEntryPost.delete().where(JamEntryPost.post == post).execute()
        for e in entries:
            entry = JamEntry.get_or_none(JamEntry.id == e["id"])
            if entry is None:
                # just skip for now
                continue
            JamEntryPost.create(entry=entry, post=post)
