import datetime
from flask import Blueprint, jsonify, request
from src.model.models import Vote, User, Post, Comment, Blog
from src.auth import get_user_from_request, login_required
from src import errors
from src.utils import doc_sample


bp = Blueprint('vote', __name__, url_prefix='/votes/')


@login_required
@bp.route("/", methods=['POST'])
@doc_sample(body={
    'target_id': 0,
    'target_type': "user or blog or post or comment",
    'value': 1
})
def vote():
    '''
    Добавить голос.
    '''
    user = get_user_from_request()

    json = request.get_json()

    t_id = json['target_id']
    t_type = 0
    if json['target_type'] == 'user':
        user = User.get_or_none(User.id == t_id)
        if user is None:
            return errors.vote_no_target()
        t_type = 1
    elif json['target_type'] == 'blog':
        blog = Blog.get_or_none(Blog.id == t_id)
        if blog is None:
            return errors.vote_no_target()
        t_type = 2
    elif json['target_type'] == 'post':
        post = Post.get_or_none(Post.id == t_id)
        if post is None:
            return errors.vote_no_target()
        t_type = 3
    elif json['target_type'] == 'comment':
        comment = Comment.get_or_none(Comment.id == t_id)
        if comment is None:
            return errors.vote_no_target()
        t_type = 4
    else:
        return errors.vote_no_target_type()

    value = json['value']
    if value > 0:
        value = 1
    elif value < 0:
        value = -1
    else:
        value = 0

    vote = Vote.get_or_none(
        Vote.voter == user,
        target_id=t_id,
        target_type=t_type)
    if vote:
        vote.vote_value = value
        vote.updated_date = datetime.datetime.now()
    else:
        vote = Vote(
            created_date=datetime.datetime.now(),
            updated_date=datetime.datetime.now(),
            voter=user,
            target_id=t_id,
            target_type=t_type,
            vote_value=value,
        )

    vote.save()

    return jsonify({
        'success': 1,
        'vote': vote.to_json(),
    })
