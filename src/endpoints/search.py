from flask import Blueprint, jsonify, request
from playhouse.flask_utils import PaginatedQuery
from src.model.models import Blog, Post, User, Vote
from src import errors
from src.auth import get_user_from_request

bp = Blueprint("search", __name__, url_prefix="/search/")


@bp.route("/", methods=["GET"])
def get():
    search_type = request.args.get("type")
    search_query = request.args.get("q")
    limit = max(1, min(int(request.args.get("limit") or 20), 100))

    type = 0

    if not search_query or len(search_query) == 0:
        return errors.wrong_payload("q")

    if search_type == "post":
        query = Post.get_public_posts().where(
            Post.title.contains(search_query) | Post.text.contains(search_query)
        )
        type = 3
    elif search_type == "blog":
        query = Blog.get_public_blogs().where(
            Blog.title.contains(search_query) | Blog.description.contains(search_query)
        )
        type = 2
    elif search_type == "user":
        query = User.select().where(
            User.username.contains(search_query) | User.name.contains(search_query)
        )
        type = 1
    else:
        return errors.wrong_payload("type")

    paginated_query = PaginatedQuery(query, paginate_by=limit)
    items = [item.to_json() for item in paginated_query.get_object_list()]
    items = [Vote.add_votes_info(i, type, get_user_from_request()) for i in items]

    return jsonify(
        {
            "success": 1,
            "result": items,
            "meta": {"page_count": paginated_query.get_page_count()},
        }
    )
