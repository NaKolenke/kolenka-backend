from converters.models import TuTalk, TuUser, TuComment, TuTalkUser
from src import create_app
from converters import content
from src.model.models import Conversation, User, Message, ConversationParticipiant


def convert():
    create_app()

    for t in TuTalk.select():
        creator = User.get_or_none(User.id == t.user)
        if not creator:
            print("Skipped talk. Owner:" + TuUser.get(TuUser.user == t.user).user_login)
            continue

        conversation = Conversation.create(
            id=t.talk, creator=creator, created_date=t.talk_date, title=t.talk_title
        )

        text = content.replace_uploads_in_text(creator, t.talk_text)

        # тут возможно надо будет перенести текст в объект conversation
        Message.create(
            id=t.talk,
            conversation=conversation,
            creator=creator,
            parent=None,
            level=0,
            created_date=t.talk_date,
            updated_date=t.talk_date,
            text=text,
        )

    for c in TuComment.select():
        if c.target_type != "talk":
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

        Message.create(
            id=c.comment,
            conversation=Conversation.get(c.target),
            creator=creator,
            parent=Message.get(Message.id == c.comment_pid),
            level=c.comment_level,
            created_date=c.comment_date,
            updated_date=updated,
            text=text,
        )

    for t in TuTalkUser.select():
        user = User.get_or_none(User.id == t.user)

        if not user:
            print(
                "Skipped user participiation. Owner:"
                + TuUser.get(TuUser.user == t.user).user_login
            )
            continue

        conversation = Conversation.get(Conversation.id == t.talk)

        ConversationParticipiant.create(user=user, conversation=conversation)
