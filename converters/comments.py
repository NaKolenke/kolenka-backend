from converters import content
from converters.models import TuComment, TuUser
from src import create_app
from src.model.models import Comment, Post, User


def convert():
    create_app()

    for c in TuComment.select():
        if c.target_type != "topic":
            continue

        creator = User.get_or_none(User.id == c.user)
        if not creator:
            print(
                "Skipped comment. Owner:" + TuUser.get(TuUser.user == c.user).user_login
            )
            continue

        updated = c.comment_date
        if not updated:
            updated = c.comment_date_edit

        text = content.replace_uploads_in_text(creator, c.comment_text)

        post = Post.get_or_none(Post.id == c.target)
        if post is None:
            print("Skipped comment " + str(c.comment) + ". No post" + str(c.target))
            continue

        parent = None
        if c.comment_pid:
            parent = Comment.get_or_none(Comment.id == c.comment_pid)
            if parent is None:
                print("Skipped comment " + str(c.comment) + ". No parent")

        Comment.create(
            id=c.comment,
            post=post,
            creator=creator,
            parent=parent,
            level=c.comment_level,
            created_date=c.comment_date,
            updated_date=updated,
            text=text,
            rating=0,
        )
