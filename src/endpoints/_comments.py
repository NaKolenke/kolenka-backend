import datetime

from flask import jsonify

from src import errors
from src.model.models import Comment, Vote
from src.utils import sanitize


def _get_comments(type, object_id, user):
    query = Comment.get_comments_for(type, object_id)
    comments = [c.to_json() for c in query]
    comments = [Vote.add_votes_info(c, 4, user) for c in comments]

    return jsonify({"success": 1, "comments": comments})


def _add_comment(type, object_id, user, text, parent_comment_id=None):
    text = sanitize(text)

    parent = None
    level = 0
    if parent_comment_id:
        parent = Comment.get_or_none(Comment.id == parent_comment_id)
        if parent is not None:
            level = parent.level + 1

    comment = Comment.create(
        object_type=type,
        object_id=object_id,
        created_date=datetime.datetime.now(),
        updated_date=datetime.datetime.now(),
        creator=user,
        text=text,
        parent=parent,
        level=level,
    )

    return comment


def _edit_comment(comment_id, user, text):
    comment = Comment.get_or_none(Comment.id == comment_id)
    if comment is None:
        return errors.not_found()

    is_accessible = user.is_admin or comment.creator == user
    if not is_accessible:
        return errors.no_access()

    comment.text = sanitize(text)
    comment.save()

    return comment
