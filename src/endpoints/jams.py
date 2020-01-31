import datetime
from flask import Blueprint, jsonify, request
from playhouse.flask_utils import PaginatedQuery
from src.auth import login_required, get_user_from_request
from src.model.models import Jam, Blog, BlogParticipiation, Content
from src import errors
from src.utils import sanitize, doc_sample


bp = Blueprint("jams", __name__, url_prefix="/jams/")


@bp.route("/", methods=["GET"])
def get_jams():
    """Получить список джемов"""
    query = Jam.get_all_jams()
    limit = max(1, min(int(request.args.get("limit") or 20), 100))
    paginated_query = PaginatedQuery(query, paginate_by=limit)

    jams = [j.to_json() for j in paginated_query.get_object_list()]
    return jsonify(
        {
            "success": 1,
            "jams": jams,
            "meta": {"page_count": paginated_query.get_page_count()},
        }
    )


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
    image = json.get("image", None)
    start_date = json.get("start_date", None)
    end_date = json.get("end_date", None)

    blog = create_blog_for_jam(user, title, url, image)

    jam = Jam.create(
        created_date=datetime.datetime.now(),
        updated_date=datetime.datetime.now(),
        creator=user,
        blog=blog,
        title=title,
        url=url,
        description=sanitize(description),
        short_description=sanitize(short_description),
        start_date=start_date,
        end_date=end_date,
    )

    if image:
        jam.logo = Content.get_or_none(Content.id == image)

    jam.save()

    return jsonify({"success": 1, "jam": jam.to_json()})


@bp.route("/<id>/", methods=["POST"])
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
def edit_jam(id):
    """Редактировать джем"""
    user = get_user_from_request()
    jam = Jam.get_or_none(id == id)

    if jam is None:
        return errors.not_found()

    if jam.creator != user:
        return errors.no_access()

    json = request.json

    title = json.get("title", jam.title)
    url = json.get("url", jam.url)
    description = json.get("description", jam.description)
    short_description = json.get("short_description", jam.short_description)

    start_date = json.get("start_date", jam.start_date)
    end_date = json.get("end_date", jam.end_date)

    image = None
    if jam.logo is not None:
        image = json.get("image", jam.logo.id)

    edit_blog_for_jam(jam.blog, title, url, image)

    jam.title = title
    jam.url = url
    jam.description = sanitize(description)
    jam.short_description = sanitize(short_description)
    jam.start_date = start_date
    jam.end_date = end_date

    if image:
        jam.logo = Content.get_or_none(Content.id == image)

    jam.updated_date = datetime.datetime.now()
    jam.save()

    return jsonify({"success": 1, "jam": jam.to_json()})


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
    blog.url = url
    if image:
        blog.image = Content.get_or_none(Content.id == image)

    blog.updated_date = datetime.datetime.now()
    blog.save()

    return blog
