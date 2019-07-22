import datetime
import secrets
from peewee import \
    IntegerField, \
    BigIntegerField, \
    CharField, \
    TextField, \
    ForeignKeyField, \
    DateTimeField, \
    DateField, \
    BooleanField, \
    fn, \
    JOIN
from playhouse.shortcuts import model_to_dict

from src.model import db


def get_exclude():
    return [User.password, User.email, Content.user, Content.path]


class DatabaseInfo(db.db_wrapper.Model):
    version = IntegerField()


class Content(db.db_wrapper.Model):
    user = IntegerField()
    path = CharField()
    mime = CharField()
    size = BigIntegerField()

    def to_json(self):
        content_dict = model_to_dict(self, exclude=get_exclude())
        return content_dict

    @property
    def is_image(self):
        return "image/" in self.mime

    @property
    def is_small_image(self):
        return self.is_image and self.size < 1024 * 25  # 25 kb?

    @classmethod
    def get_user_files(cls, user):
        return cls.select().where(Content.user == user)


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

    def to_json(self):
        user_dict = model_to_dict(self, exclude=get_exclude())
        return user_dict

    def to_json_with_email(self):
        user_dict = model_to_dict(self, exclude=[User.password, Content.user])
        return user_dict

    @classmethod
    def get_admins(cls):
        return cls.select().where(User.is_admin == True)  # noqa E712


class Token(db.db_wrapper.Model):
    user = ForeignKeyField(model=User, backref='tokens')
    token = CharField()
    valid_until = DateTimeField()
    is_refresh_token = BooleanField() # deprecated
    token_type = CharField()

    @classmethod
    def generate_access_token(cls, user):
        vu = datetime.datetime.now() + datetime.timedelta(days=30)
        return cls.create(
                user=user,
                token=secrets.token_hex(),
                token_type='access',
                valid_until=vu)

    @classmethod
    def generate_refresh_token(cls, user):
        vu = datetime.datetime.now() + datetime.timedelta(days=90)
        return cls.create(
                user=user,
                token=secrets.token_hex(),
                token_type='refresh',
                valid_until=vu)

    @classmethod
    def generate_recover_token(cls, user):
        vu = datetime.datetime.now() + datetime.timedelta(days=1)
        return cls.create(
                user=user,
                token=secrets.token_hex(),
                token_type='recover',
                valid_until=vu)


class Feedback(db.db_wrapper.Model):
    user = ForeignKeyField(model=User, backref='feedbacks')
    text = TextField()
    is_resolved = BooleanField(default=False)

    def to_json(self):
        feedback_dict = model_to_dict(self, exclude=get_exclude())
        return feedback_dict


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
    def get_public_blogs(cls):
        readers = fn.COUNT(BlogParticipiation.id)
        return cls.select(Blog, readers.alias('readers')) \
            .join(BlogParticipiation, JOIN.LEFT_OUTER).where(
                Blog.blog_type != 3
            ).group_by(Blog.id).order_by(readers.desc())

    @classmethod
    def get_readers_count(cls, blog):
        return cls.get_readers(blog).count()

    @classmethod
    def get_readers(cls, blog):
        return User.select().join(BlogParticipiation).where(
            BlogParticipiation.blog == blog
        )

    @classmethod
    def get_blogs_for_user(cls, user):
        readers = fn.COUNT(BlogParticipiation.id)
        return cls.select(Blog, readers.alias('readers')) \
            .join(BlogParticipiation, JOIN.LEFT_OUTER).where(
                (BlogParticipiation.user == user) &
                (Blog.blog_type != 3)
            ).group_by(Blog.id).order_by(readers.desc())

    @classmethod
    def get_user_role(cls, blog, user):
        query = BlogParticipiation.select().where(
                (BlogParticipiation.user == user) &
                (BlogParticipiation.blog == blog)
            )

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

    def to_json(self):
        blog_dict = model_to_dict(self, exclude=get_exclude())
        blog_dict['readers'] = Blog.get_readers_count(self)
        return blog_dict


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
    def get_public_posts(cls):
        return cls.select().join(Blog).where(
            # (Post.is_on_main) &
            (Post.is_draft == False) &  # noqa: E712
            (Blog.blog_type != 3)
        ).order_by(Post.created_date.desc())

    @classmethod
    def get_posts_for_blog(cls, blog):
        return cls.select().where(
            (Post.is_draft == False) &  # noqa: E712
            (Post.blog == blog)
        ).order_by(Post.created_date.desc())

    @classmethod
    def get_user_posts(cls, user):
        return cls.select().where(
            (Post.is_draft == False) &  # noqa: E712
            (Post.creator == user)
        ).order_by(Post.created_date.desc())

    @classmethod
    def get_user_drafts(cls, user):
        return cls.select().where(
            (Post.is_draft == True) &  # noqa: E712
            (Post.creator == user)
        ).order_by(Post.created_date.desc())

    @classmethod
    def get_public_posts_with_tag(cls, tag):
        return cls.select().join(TagMark).switch(Post).join(Blog).where(
            (Post.is_draft == False) &  # noqa: E712
            (TagMark.tag == tag) &
            (Blog.blog_type != 3)
        ).order_by(Post.created_date.desc())

    def to_json(self):
        post_dict = model_to_dict(self, exclude=get_exclude())
        post_dict['comments'] = Comment.get_comments_count_for_post(self)
        return post_dict


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
    def get_comments_for_post(cls, post):
        return cls.select().where(
            Comment.post == post
        ).order_by(Comment.created_date.desc())

    @classmethod
    def get_comments_count_for_post(cls, post):
        return cls.get_comments_for_post(post).count()

    def to_json(self):
        comment_dict = model_to_dict(
            self,
            exclude=get_exclude() + [Comment.post])
        return comment_dict


class Tag(db.db_wrapper.Model):
    title = TextField()
    created_date = DateTimeField()

    @classmethod
    def get_tags(cls):
        ntags = fn.COUNT(TagMark.id)
        return (cls
                .select(Tag, ntags.alias('count'))
                .join(TagMark, JOIN.LEFT_OUTER)
                .group_by(Tag.id)
                .order_by(ntags.desc()))

    def to_json(self):
        tag_dict = model_to_dict(self, exclude=get_exclude())
        if hasattr(self, 'count'):
            tag_dict['count'] = self.count
        return tag_dict


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


class Notification(db.db_wrapper.Model):
    user = ForeignKeyField(model=User)
    text = TextField()
    object_type = TextField(default='')
    object_id = IntegerField(default=0)
    created_date = DateTimeField()
    is_new = BooleanField(default=True)

    @classmethod
    def get_user_notifications(cls, user):
        return cls.select().where(
            (Notification.user == user)
        ).order_by(Notification.created_date.desc())

    @classmethod
    def get_user_unread_notifications(cls, user):
        return cls.select().where(
            (Notification.user == user) &
            (Notification.is_new == True)  # noqa E712
        ).order_by(Notification.created_date.desc())

    @classmethod
    def mark_notification_as_readed(cls, user, notification_id):
        notification = cls.get_or_none(
            (Notification.user == user) &
            (Notification.id == notification_id)
        )
        if notification is not None:
            notification.is_new = False
            notification.save()

    def to_json(self):
        not_dict = model_to_dict(
            self,
            exclude=get_exclude() + [Notification.user])
        return not_dict


class Sticker(db.db_wrapper.Model):
    name = TextField()
    file = ForeignKeyField(model=Content)

    def to_json(self):
        return model_to_dict(self, exclude=[Content.user])


class Page(db.db_wrapper.Model):
    title = TextField()
    body = TextField()
    creator = ForeignKeyField(model=User)
    updater = ForeignKeyField(model=User)
    created_date = DateTimeField()
    updated_date = DateTimeField()
