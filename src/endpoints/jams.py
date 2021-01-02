import datetime
import uuid

from flask import Blueprint, jsonify, request
from playhouse.flask_utils import PaginatedQuery

from src import errors
from src.auth import get_user_from_request, login_required
from src.endpoints._comments import _add_comment, _edit_comment, _get_comments
from src.model.models import (
    Blog,
    BlogParticipiation,
    Comment,
    Content,
    Jam,
    JamCriteria,
    JamEntry,
    JamEntryLink,
    JamEntryVote,
    Notification,
)
from src.utils import doc_sample, sanitize

bp = Blueprint("jams", __name__, url_prefix="/jams/")


@bp.route("/", methods=["GET"])
def get_jams():
    """Получить список джемов"""
    query = Jam.get_current_jams()
    current_jams = [_jam_to_json(j) for j in query]

    query = Jam.get_closest_jams()
    closest_jams = [_jam_to_json(j) for j in query]

    query = Jam.get_closed_jams()
    limit = max(1, min(int(request.args.get("limit") or 20), 100))
    paginated_query = PaginatedQuery(query, paginate_by=limit)

    closed_jams = [_jam_to_json(j) for j in paginated_query.get_object_list()]
    return jsonify(
        {
            "success": 1,
            "jams": {
                "current": current_jams,
                "closest": closest_jams,
                "closed": closed_jams,
            },
            "meta": {"page_count": paginated_query.get_page_count()},
        }
    )


@bp.route("/<url>/", methods=["GET"])
def get_jam(url):
    """Получить джем по указанному url"""
    jam = Jam.get_or_none(Jam.url == url)
    if jam is None:
        return errors.not_found()

    jam_dict = _jam_to_json(jam)

    return jsonify({"success": 1, "jam": jam_dict})


@bp.route("/", methods=["POST"])
@login_required
@doc_sample(
    body={
        "title": "some title",
        "url": "some url",
        "description": "some description",
        "short_description": "some description",
        "start_date": "date",
        "end_date": "date",
        "logo": "content id",
    }
)
def create_jam():
    """Создать джем"""
    user = get_user_from_request()

    json = request.json
    required_fields = ["title", "url", "description", "short_description"]
    missed_fields = []
    for field in required_fields:
        if field not in json:
            missed_fields.append(field)
    if len(missed_fields) > 0:
        return errors.wrong_payload(missed_fields)

    title = json["title"]
    url = json["url"]
    description = json["description"]
    short_description = json["short_description"]
    image = json.get("logo", None)
    start_date = json.get("start_date", None)
    end_date = json.get("end_date", None)
    criterias = json.get("criterias", [])

    if Jam.get_or_none(Jam.url == url) is not None:
        return errors.jam_url_already_taken()

    blog = create_blog_for_jam(user, title, url, image)

    jam = Jam.create(
        created_date=datetime.datetime.now(),
        updated_date=datetime.datetime.now(),
        creator=user,
        blog=blog,
        title=title,
        url=url,
        short_description=sanitize(short_description),
        description=sanitize(description),
        start_date=start_date,
        end_date=end_date,
    )

    if image:
        jam.logo = Content.get_or_none(Content.id == image)

    jam.save()

    for criteria in criterias:
        JamCriteria.create(jam=jam, title=criteria["title"], order=criteria["order"])

    return jsonify({"success": 1, "jam": jam.to_json()})


@bp.route("/<url>/", methods=["POST"])
@login_required
@doc_sample(
    body={
        "title": "some title",
        "url": "some url",
        "description": "some description",
        "short_description": "some description",
        "start_date": "date",
        "end_date": "date",
        "logo": "content id",
    }
)
def edit_jam(url):
    """Редактировать джем"""
    user = get_user_from_request()
    jam = Jam.get_or_none(Jam.url == url)

    if jam is None:
        return errors.not_found()

    if jam.creator != user:
        return errors.no_access()

    json = request.json

    title = json.get("title", jam.title)
    # url = json.get("url", jam.url)
    description = json.get("description", jam.description)
    short_description = json.get("short_description", jam.short_description)
    start_date = json.get("start_date", jam.start_date)
    end_date = json.get("end_date", jam.end_date)
    criterias = json.get("criterias", [])

    image = None
    if "image" in json:
        image = json["image"]

    edit_blog_for_jam(jam.blog, title, url, image)

    jam.title = title
    # jam.url = url
    jam.description = sanitize(description)
    jam.short_description = sanitize(short_description)
    jam.start_date = start_date
    jam.end_date = end_date

    if image:
        jam.logo = Content.get_or_none(Content.id == image)

    jam.updated_date = datetime.datetime.now()
    jam.save()

    JamCriteria.delete().where(JamCriteria.jam == jam).execute()
    for criteria in criterias:
        JamCriteria.create(jam=jam, title=criteria["title"], order=criteria["order"])

    return jsonify({"success": 1, "jam": jam.to_json()})


@bp.route("/<url>/participiate/", methods=["POST"])
@login_required
@doc_sample(body={})
def participiate(url):
    """Участвовать в джеме"""
    user = get_user_from_request()
    jam = Jam.get_or_none(Jam.url == url)

    if jam is None:
        return errors.not_found()
    entry = JamEntry.get_or_none(jam=jam, creator=user)
    if not entry:
        JamEntry.create(
            jam=jam,
            creator=user,
            created_date=datetime.datetime.now(),
            url=uuid.uuid4(),
        )
    else:
        entry.is_archived = False
        entry.save()

    return jsonify({"success": 1})


@bp.route("/<url>/leave/", methods=["POST"])
@login_required
@doc_sample(body={})
def leave(url):
    """Не участвовать в джеме"""
    user = get_user_from_request()
    jam = Jam.get_or_none(Jam.url == url)

    if jam is None:
        return errors.not_found()

    entry = JamEntry.get_or_none(jam=jam, creator=user)
    if entry:
        entry.is_archived = True
        entry.save()

    return jsonify({"success": 1})


@bp.route("/<url>/start/", methods=["POST"])
@login_required
@doc_sample(body={})
def start(url):
    """Запустить джем"""

    user = get_user_from_request()
    jam = Jam.get_or_none(Jam.url == url)

    if jam is None:
        return errors.not_found()

    if jam.creator != user:
        return errors.no_access()

    jam.status = 1
    jam.save()

    return jsonify({"success": 1})


@bp.route("/<url>/finish/", methods=["POST"])
@login_required
@doc_sample(body={})
def finish(url):
    """Закончить джем"""
    user = get_user_from_request()
    jam = Jam.get_or_none(Jam.url == url)

    if jam is None:
        return errors.not_found()

    if jam.creator != user:
        return errors.no_access()

    jam.status = 2
    jam.save()

    return jsonify({"success": 1})


@bp.route("/<url>/entries/", methods=["GET"])
@login_required
@doc_sample(body={})
def jam_entries(url):
    """Получить список заявок на джем"""
    jam = Jam.get_or_none(Jam.url == url)

    if jam is None:
        return errors.not_found()

    entries = JamEntry.select().where(JamEntry.jam == jam)
    entries = [_entry_to_json(entry) for entry in entries]

    return jsonify({"success": 1, "entries": entries})


@bp.route("/<url>/entry/my/", methods=["GET"])
@login_required
@doc_sample(body={})
def my_entry(url):
    """Получить заявку на джем от текущего пользователя"""
    user = get_user_from_request()
    jam = Jam.get_or_none(Jam.url == url)

    if jam is None:
        return errors.not_found()

    entry = JamEntry.get_or_none(jam=jam, creator=user)

    return jsonify({"success": 1, "entry": _entry_to_json(entry)})


@bp.route("/<url>/entry/<entry_url>/", methods=["GET"])
@login_required
@doc_sample(body={})
def jam_entry(url, entry_url):
    """Получить заявку на джем по ссылке"""
    jam = Jam.get_or_none(Jam.url == url)

    if jam is None:
        return errors.not_found()

    entry = JamEntry.get_or_none(JamEntry.url == entry_url)

    if entry is None:
        return errors.not_found()

    return jsonify({"success": 1, "entry": _entry_to_json(entry)})


@bp.route("/<url>/entry/<entry_url>/criterias/", methods=["GET"])
@login_required
@doc_sample(body={})
def get_criterias(url, entry_url):
    """Получить оценки для заявки на джем"""
    jam = Jam.get_or_none(Jam.url == url)

    if jam is None:
        return errors.not_found()

    entry = JamEntry.get_or_none(JamEntry.url == entry_url)

    if entry is None:
        return errors.not_found()

    criterias = JamEntryVote.select().where(
        (JamEntryVote.entry == entry) & (JamEntryVote.voter == get_user_from_request())
    )
    return jsonify({"success": 1, "criterias": _criterias_to_json(criterias)})


@bp.route("/<url>/entry/<entry_url>/criterias/", methods=["POST"])
@login_required
@doc_sample(body={})
def add_votes(url, entry_url):
    """Получить оценки для заявки на джем"""
    jam = Jam.get_or_none(Jam.url == url)

    if jam is None:
        return errors.not_found()

    entry = JamEntry.get_or_none(JamEntry.url == entry_url)

    if entry is None:
        return errors.not_found()

    JamEntryVote.delete().where(
        (JamEntryVote.entry == entry) & (JamEntryVote.voter == get_user_from_request())
    ).execute()

    json = request.json

    json_criterias = json
    for criteria_id, vote in json_criterias.items():
        JamEntryVote.create(
            entry=entry, voter=get_user_from_request(), vote=vote, criteria=criteria_id,
        )

    return jsonify({"success": 1})


@bp.route("/<url>/entry/my/", methods=["POST"])
@login_required
@doc_sample(body={})
def edit_my_entry(url):
    """Редактировать заявку на джем от текущего пользователя"""
    user = get_user_from_request()
    jam = Jam.get_or_none(Jam.url == url)

    if jam is None:
        return errors.not_found()

    entry = JamEntry.get_or_none(jam=jam, creator=user)
    if entry is None:
        return errors.not_found()

    json = request.json

    title = json.get("title", entry.title)
    url = json.get("url", entry.url)
    description = json.get("info", entry.info)
    short_description = json.get("short_info", entry.short_info)
    links = json.get("links", [])

    has_entry_with_same_url = False
    entries_with_same_url = JamEntry.select().where(
        (JamEntry.url == url) & (JamEntry.jam == jam)
    )
    for e in entries_with_same_url:
        if e.id != entry.id:
            has_entry_with_same_url = True

    if has_entry_with_same_url:
        return errors.jam_entry_url_already_taken()

    image = None
    if "logo" in json:
        image = json["logo"]

    entry.title = title
    entry.url = url
    entry.info = sanitize(description)
    entry.short_info = sanitize(short_description)

    if image:
        entry.logo = Content.get_or_none(Content.id == image)

    JamEntryLink.delete().where(JamEntryLink.entry == entry).execute()
    for link in links:
        JamEntryLink.create(
            entry=entry, title=link["title"], href=link["href"], order=link["order"],
        )

    entry.save()

    return jsonify({"success": 1, "entry": _entry_to_json(entry)})


@login_required
@bp.route("/<url>/comments/", methods=["GET", "POST"])
def comments(url):
    """Получить список комментариев для джема или добавить новый комментарий"""
    jam = Jam.get_or_none(Jam.url == url)
    if jam is None:
        return errors.not_found()

    if request.method == "GET":
        user = get_user_from_request()
        # if jam.is_draft:

        #     if user is None:
        #         return errors.no_access()

        #     if jam.creator != user:
        #         return errors.no_access()
        return _get_comments("jam", jam.id, user)
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

        comment = _add_comment("jam", jam.id, user, text, parent_id)

        if user.id != jam.creator.id:
            t = "Пользователь {0} оставил комментарий к джему {1}: {2}"
            notification_text = t.format(user.visible_name, jam.title, text)

            Notification.create(
                user=jam.creator,
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
@bp.route("/<url>/comments/<comment_id>", methods=["PUT"])
def edit_comment(url, comment_id):
    """Редактировать комментарий"""
    jam = Jam.get_or_none(Jam.url == url)
    if jam is None:
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


@login_required
@bp.route("/<url>/entry/<entry_url>/comments/", methods=["GET", "POST"])
def comments_in_entry(url, entry_url):
    """Получить список комментариев для джема или добавить новый комментарий"""
    jam = Jam.get_or_none(Jam.url == url)
    if jam is None:
        return errors.not_found()

    entry = JamEntry.get_or_none(JamEntry.url == entry_url)

    if entry is None:
        return errors.not_found()

    if request.method == "GET":
        user = get_user_from_request()
        # if jam.is_draft:

        #     if user is None:
        #         return errors.no_access()

        #     if jam.creator != user:
        #         return errors.no_access()
        return _get_comments("jam_entry", entry.id, user)
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

        comment = _add_comment("jam_entry", entry.id, user, text, parent_id)

        if user.id != jam.creator.id:
            t = "Пользователь {0} оставил комментарий к заявке на джем {1}: {2}"
            notification_text = t.format(user.visible_name, jam.title, text)

            Notification.create(
                user=jam.creator,
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
@bp.route("/<url>/entry/<entry_url>/comments/<comment_id>/", methods=["PUT"])
def edit_comment_in_entry(url, entry_url, comment_id):
    """Редактировать комментарий"""
    jam = Jam.get_or_none(Jam.url == url)
    if jam is None:
        return errors.not_found()

    entry = JamEntry.get_or_none(JamEntry.url == entry_url)

    if entry is None:
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


def create_blog_for_jam(user, title, url, image=None):
    blog = Blog.create(
        created_date=datetime.datetime.now(),
        updated_date=datetime.datetime.now(),
        creator=user,
    )
    BlogParticipiation.create(blog=blog, user=user, role=1)

    blog.title = title
    blog.description = f'Это блог для джема "{title}"'
    blog.url = url
    blog.blog_type = 1
    if image:
        blog.image = Content.get_or_none(Content.id == image)

    blog.updated_date = datetime.datetime.now()
    blog.save()

    return blog


def edit_blog_for_jam(blog, title, url, image=None):
    blog.title = title
    blog.description = f'Это блог для джема "{title}"'
    # blog.url = url
    if image:
        blog.image = Content.get_or_none(Content.id == image)

    blog.updated_date = datetime.datetime.now()
    blog.save()

    return blog


def _jam_to_json(jam):
    jam_dict = jam.to_json()

    jam_dict["is_participiating"] = False
    user = get_user_from_request()
    if user:
        entry = JamEntry.get_or_none(jam=jam, creator=user)
        if entry:
            jam_dict["is_participiating"] = True

    jam_dict["participators"] = JamEntry.select().where(JamEntry.jam == jam).count()

    return jam_dict


def _entry_to_json(entry):
    entry_dict = entry.to_json()

    return entry_dict


def _criterias_to_json(criterias):
    jsons = [c.to_json() for c in criterias]

    return jsons
