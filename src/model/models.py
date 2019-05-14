import datetime
import secrets
from peewee import \
    IntegerField, \
    CharField, \
    TextField, \
    ForeignKeyField, \
    DateTimeField, \
    DateField, \
    BooleanField

from src.model import db


class DatabaseInfo(db.db_wrapper.Model):
    version = IntegerField()


class Content(db.db_wrapper.Model):
    user = IntegerField()
    path = CharField()


class User(db.db_wrapper.Model):
    username = CharField(unique=True)
    password = CharField()
    email = CharField()
    registration_date = DateTimeField()
    last_active_date = DateTimeField()
    name = CharField(null=True)
    birthday = DateField(null=True)
    about = TextField(null=True)
    is_admin = BooleanField(default=False)

    avatar = ForeignKeyField(model=Content, backref='avatar', null=True)


class Token(db.db_wrapper.Model):
    user = ForeignKeyField(model=User, backref='tokens')
    token = CharField()
    valid_until = DateTimeField()
    is_refresh_token = BooleanField()

    @classmethod
    def generate_access_token(cls, user):
        vu = datetime.datetime.now() + datetime.timedelta(days=30)
        return cls.create(
                user=user, token=secrets.token_hex(), is_refresh_token=False,
                valid_until=vu)

    @classmethod
    def generate_refresh_token(cls, user):
        vu = datetime.datetime.now() + datetime.timedelta(days=90)
        return cls.create(
                user=user, token=secrets.token_hex(), is_refresh_token=True,
                valid_until=vu)


class Feedback(db.db_wrapper.Model):
    user = ForeignKeyField(model=User, backref='feedbacks')
    text = TextField()
    is_resolved = BooleanField(default=False)


class Blog(db.db_wrapper.Model):
    image = ForeignKeyField(model=Content, backref='blogs', null=True)
    created_date = DateTimeField()
    updated_date = DateTimeField()
    description = TextField(null=True)
    title = TextField(null=True)
    url = CharField(null=True, unique=True)

    blog_type = IntegerField(choices=[
        (1, 'open'),  # Visible in list. Everyone can join and write.
        (2, 'close'),  # Visible in list.
        # Writers can join only if invited by other user. Everyone can read
        (3, 'hidden'),  # Not visible in list.
        # Read and write can only invited users.
    ], default=1)

    creator = ForeignKeyField(model=User, backref='blogs')

    @classmethod
    def get_readers_count(cls, blog):
        return cls.get_readers(blog).count()

    @classmethod
    def get_readers(cls, blog):
        return User \
            .select()   \
            .join(BlogParticipiation)   \
            .where(BlogParticipiation.blog == blog)

    @classmethod
    def get_blogs_for_user(cls, user):
        return Blog \
            .select()   \
            .join(BlogParticipiation)   \
            .where(
                (BlogParticipiation.user == user) &
                (Blog.blog_type != 3)
                )

    @classmethod
    def get_user_role(cls, blog, user):
        query = BlogParticipiation \
            .select()   \
            .where(
                (BlogParticipiation.user == user)
                & (BlogParticipiation.blog == blog))

        if query.count() == 0:
            return None

        participiation = query.get()
        return participiation.role

    @classmethod
    def has_access(cls, blog, user):
        if blog.blog_type == 3:
            if user is None:
                return False
            role = Blog.get_user_role(blog, user)
            if role is None:
                return False
        return True


class BlogParticipiation(db.db_wrapper.Model):
    blog = ForeignKeyField(model=Blog)
    user = ForeignKeyField(model=User)
    role = IntegerField(choices=[
        (1, 'owner'),
        (2, 'writer'),
        (3, 'reader'),
    ], default=1)


class BlogInvite(db.db_wrapper.Model):
    blog = ForeignKeyField(model=Blog)
    user_from = ForeignKeyField(model=User)
    user_to = ForeignKeyField(model=User)
    is_accepted = BooleanField(default=False)
    role = IntegerField(choices=[
        (1, 'owner'),
        (2, 'writer'),
        (3, 'reader'),
    ], default=1)


class Post(db.db_wrapper.Model):
    blog = ForeignKeyField(model=Blog, null=True)
    creator = ForeignKeyField(model=User)
    created_date = DateTimeField()
    updated_date = DateTimeField()
    title = TextField(null=True)
    cut_text = TextField(null=True)
    text = TextField(null=True)
    rating = IntegerField(default=0)
    is_draft = BooleanField(default=True)
    is_on_main = BooleanField(default=False)
    reads = IntegerField(default=0)
    url = CharField(null=True, unique=True)
    has_cut = BooleanField(default=False)
    cut_name = CharField(default=None, null=True)

    @classmethod
    def get_posts_for_blog(cls, blog):
        return Post \
            .select()   \
            .where(Post.blog == blog)

    @classmethod
    def get_posts_for_user(cls, user):
        return Post \ 
            .select() \
            .where(Post.creator == user)


class Comment(db.db_wrapper.Model):
    post = ForeignKeyField(model=Post)
    creator = ForeignKeyField(model=User)
    parent = ForeignKeyField(model='self', default=None, null=True)
    level = IntegerField(default=0)
    created_date = DateTimeField()
    updated_date = DateTimeField()
    text = TextField()
    rating = IntegerField(default=0)

    @classmethod
    def get_comments_count_for_post(cls, post):
        return Comment \
            .select() \
            .where(Comment.post == post) \
            .count()


class Tag(db.db_wrapper.Model):
    title = TextField()
    created_date = DateTimeField()


class TagMark(db.db_wrapper.Model):
    tag = ForeignKeyField(model=Tag)
    post = ForeignKeyField(model=Post)


class Conversation(db.db_wrapper.Model):
    creator = ForeignKeyField(model=User)
    created_date = DateTimeField()
    title = TextField()


class ConversationParticipiant(db.db_wrapper.Model):
    user = ForeignKeyField(model=User)
    conversation = ForeignKeyField(model=Conversation)


class Message(db.db_wrapper.Model):
    conversation = ForeignKeyField(model=Conversation)
    creator = ForeignKeyField(model=User)
    parent = ForeignKeyField(model='self', default=None)
    level = IntegerField(default=0)
    created_date = DateTimeField()
    updated_date = DateTimeField()
    text = TextField()
