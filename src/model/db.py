from playhouse.flask_utils import FlaskDB

db_wrapper = FlaskDB()


def init_database(app):
    global db_wrapper
    db_wrapper.init_app(app)


def create_tables():
    global db_wrapper

    from src.model.models import User, Token, Content, Feedback, Blog,\
        BlogParticipiation, BlogInvite, Post, Comment, Tag, TagMark,\
        Conversation, ConversationParticipiant, Message, DatabaseInfo,\
        Notification, Sticker

    db_wrapper.database.create_tables([
        User,
        Token,
        Content,
        Feedback,
        Blog,
        BlogParticipiation,
        BlogInvite,
        Post,
        Comment,
        Tag,
        TagMark,
        Conversation,
        ConversationParticipiant,
        Message,
        DatabaseInfo,
        Notification,
        Sticker,
        Page
    ])

    db_wrapper.database.close()


def get_database():
    global db_wrapper
    return db_wrapper.database
