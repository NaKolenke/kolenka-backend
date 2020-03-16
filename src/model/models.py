import datetime
import secrets
from peewee import (
    IntegerField,
    BigIntegerField,
    CharField,
    TextField,
    ForeignKeyField,
    DateTimeField,
    DateField,
    BooleanField,
    fn,
    JOIN,
)
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

    avatar = ForeignKeyField(model=Content, backref="avatar", null=True)

    @classmethod
    def get_admins(cls):
        return cls.select().where(User.is_admin == True)  # noqa E712

    @classmethod
    def get_users_sorted_by_active_date(cls):
        return cls.select().order_by(User.last_active_date.desc())

    @property
    def visible_name(self):
        if self.name is not None and len(self.name) > 0:
            return self.name
        return self.username

    def to_json(self):
        user_dict = model_to_dict(self, exclude=get_exclude())

        return user_dict

    def to_json_with_email(self):
        user_dict = model_to_dict(self, exclude=[User.password, Content.user])
        return user_dict


class Token(db.db_wrapper.Model):
    user = ForeignKeyField(model=User, backref="tokens")
    token = CharField()
    valid_until = DateTimeField()
    is_refresh_token = BooleanField()  # deprecated
    token_type = CharField()

    @classmethod
    def generate_access_token(cls, user):
        vu = datetime.datetime.now() + datetime.timedelta(days=30)
        return cls.create(
            user=user,
            token=secrets.token_hex(),
            token_type="access",
            is_refresh_token=False,
            valid_until=vu,
        )

    @classmethod
    def generate_refresh_token(cls, user):
        vu = datetime.datetime.now() + datetime.timedelta(days=90)
        return cls.create(
            user=user,
            token=secrets.token_hex(),
            token_type="refresh",
            is_refresh_token=True,
            valid_until=vu,
        )

    @classmethod
    def generate_recover_token(cls, user):
        vu = datetime.datetime.now() + datetime.timedelta(days=1)
        return cls.create(
            user=user,
            token=secrets.token_hex(),
            token_type="recover",
            is_refresh_token=False,
            valid_until=vu,
        )


class Feedback(db.db_wrapper.Model):
    user = ForeignKeyField(model=User, backref="feedbacks")
    text = TextField()
    is_resolved = BooleanField(default=False)

    def to_json(self):
        feedback_dict = model_to_dict(self, exclude=get_exclude())
        return feedback_dict


class Blog(db.db_wrapper.Model):
    image = ForeignKeyField(model=Content, backref="blogs", null=True)
    created_date = DateTimeField()
    updated_date = DateTimeField()
    description = TextField(null=True)
    title = TextField(null=True)
    url = CharField(null=True, unique=True)

    blog_type = IntegerField(
        choices=[
            (1, "open"),  # Visible in list. Everyone can join and write.
            (2, "close"),  # Visible in list.
            # Writers can join only if invited by other user. Everyone can read
            (3, "hidden"),  # Not visible in list.
            # Read and write can only invited users.
        ],
        default=1,
    )

    creator = ForeignKeyField(model=User, backref="blogs")

    @classmethod
    def get_public_blogs(cls):
        readers = fn.COUNT(BlogParticipiation.id)
        return (
            cls.select(Blog, readers.alias("readers"))
            .join(BlogParticipiation, JOIN.LEFT_OUTER)
            .where(Blog.blog_type != 3)
            .group_by(Blog.id)
            .order_by(readers.desc())
        )

    @classmethod
    def get_readers_count(cls, blog):
        return cls.get_readers(blog).count()

    @classmethod
    def get_readers(cls, blog):
        return (
            User.select()
            .join(BlogParticipiation)
            .where(BlogParticipiation.blog == blog)
        )

    @classmethod
    def get_blogs_for_user(cls, user):
        readers = fn.COUNT(BlogParticipiation.id)
        return (
            cls.select(Blog, readers.alias("readers"))
            .join(BlogParticipiation, JOIN.LEFT_OUTER)
            .where((BlogParticipiation.user == user) & (Blog.blog_type != 3))
            .group_by(Blog.id)
            .order_by(readers.desc())
        )

    @classmethod
    def get_user_role(cls, blog, user):
        query = BlogParticipiation.select().where(
            (BlogParticipiation.user == user) & (BlogParticipiation.blog == blog)
        )

        if query.count() == 0:
            return None

        participiation = query.get()
        return participiation.role

    @classmethod
    def has_access(cls, blog, user):
        if user is not None and user.is_admin:
            return True

        if blog.blog_type == 3:
            if user is None:
                return False
            role = Blog.get_user_role(blog, user)
            if role is None:
                return False
        return True

    def to_json(self):
        blog_dict = model_to_dict(self, exclude=get_exclude())
        blog_dict["readers"] = Blog.get_readers_count(self)

        return blog_dict


class BlogParticipiation(db.db_wrapper.Model):
    blog = ForeignKeyField(model=Blog)
    user = ForeignKeyField(model=User)
    role = IntegerField(choices=[(1, "owner"), (2, "writer"), (3, "reader")], default=1)


class BlogInvite(db.db_wrapper.Model):
    blog = ForeignKeyField(model=Blog)
    user_from = ForeignKeyField(model=User)
    user_to = ForeignKeyField(model=User)
    is_accepted = BooleanField(default=False)
    role = IntegerField(choices=[(1, "owner"), (2, "writer"), (3, "reader")], default=1)


class Post(db.db_wrapper.Model):
    blog = ForeignKeyField(model=Blog, null=True)
    creator = ForeignKeyField(model=User)
    created_date = DateTimeField()
    updated_date = DateTimeField()
    title = TextField(null=True)
    cut_text = TextField(null=True)
    text = TextField(null=True)
    is_draft = BooleanField(default=True)
    is_on_main = BooleanField(default=False)
    reads = IntegerField(default=0)
    url = CharField(null=True, unique=True)
    has_cut = BooleanField(default=False)
    cut_name = CharField(default=None, null=True)

    @classmethod
    def get_public_posts(cls):
        return (
            cls.select()
            .join(Blog)
            .where(
                # (Post.is_on_main) &
                (Post.is_draft == False)
                & (Blog.blog_type != 3)  # noqa: E712
            )
            .order_by(Post.created_date.desc())
        )

    @classmethod
    def get_posts_for_blog(cls, blog):
        return (
            cls.select()
            .where((Post.is_draft == False) & (Post.blog == blog))  # noqa: E712
            .order_by(Post.created_date.desc())
        )

    @classmethod
    def get_user_posts(cls, user):
        return (
            cls.select()
            .where((Post.is_draft == False) & (Post.creator == user))  # noqa: E712
            .order_by(Post.created_date.desc())
        )

    @classmethod
    def get_user_drafts(cls, user):
        return (
            cls.select()
            .where((Post.is_draft == True) & (Post.creator == user))  # noqa: E712
            .order_by(Post.created_date.desc())
        )

    @classmethod
    def get_public_posts_with_tag(cls, tag):
        return (
            cls.select()
            .join(TagMark)
            .switch(Post)
            .join(Blog)
            .where(
                (Post.is_draft == False)
                & (TagMark.tag == tag)  # noqa: E712
                & (Blog.blog_type != 3)  # noqa: E712
            )
            .order_by(Post.created_date.desc())
        )

    def to_json(self):
        post_dict = model_to_dict(self, exclude=get_exclude())
        post_dict["comments"] = Comment.get_comments_count_for_post(self)
        post_dict["tags"] = [t.to_json() for t in Tag.get_for_post(self)]

        return post_dict


class Comment(db.db_wrapper.Model):
    post = ForeignKeyField(model=Post)
    creator = ForeignKeyField(model=User)
    parent = ForeignKeyField(model="self", default=None, null=True)
    level = IntegerField(default=0)
    created_date = DateTimeField()
    updated_date = DateTimeField()
    text = TextField()

    @classmethod
    def get_comments_for_post(cls, post):
        return (
            cls.select()
            .where(Comment.post == post)
            .order_by(Comment.created_date.desc())
        )

    @classmethod
    def get_comments_count_for_post(cls, post):
        return cls.get_comments_for_post(post).count()

    def to_json(self):
        comment_dict = model_to_dict(self, exclude=get_exclude() + [Comment.post])

        return comment_dict


class Tag(db.db_wrapper.Model):
    title = TextField()
    created_date = DateTimeField()

    @classmethod
    def get_tags(cls):
        ntags = fn.COUNT(TagMark.id)
        return (
            cls.select(Tag, ntags.alias("count"))
            .join(TagMark, JOIN.LEFT_OUTER)
            .group_by(Tag.id)
            .order_by(ntags.desc())
        )

    @classmethod
    def get_for_post(cls, post):
        return (
            cls.select(Tag).join(TagMark, JOIN.LEFT_OUTER).where(TagMark.post == post)
        )

    def to_json(self):
        tag_dict = model_to_dict(self, exclude=get_exclude())
        if hasattr(self, "count"):
            tag_dict["count"] = self.count
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
    parent = ForeignKeyField(model="self", default=None)
    level = IntegerField(default=0)
    created_date = DateTimeField()
    updated_date = DateTimeField()
    text = TextField()


class Notification(db.db_wrapper.Model):
    user = ForeignKeyField(model=User)
    text = TextField()
    object_type = TextField(default="")
    object_id = IntegerField(default=0)
    created_date = DateTimeField()
    is_new = BooleanField(default=True)

    @classmethod
    def get_user_notifications(cls, user):
        return (
            cls.select()
            .where((Notification.user == user))
            .order_by(Notification.created_date.desc())
        )

    @classmethod
    def get_user_unread_notifications(cls, user):
        return (
            cls.select()
            .where(
                (Notification.user == user) & (Notification.is_new == True)  # noqa E712
            )
            .order_by(Notification.created_date.desc())
        )

    @classmethod
    def mark_notification_as_readed(cls, user, notification_id):
        notification = cls.get_or_none(
            (Notification.user == user) & (Notification.id == notification_id)
        )
        if notification is not None:
            notification.is_new = False
            notification.save()

    def to_json(self):
        not_dict = model_to_dict(self, exclude=get_exclude() + [Notification.user])
        return not_dict


class Sticker(db.db_wrapper.Model):
    name = TextField()
    file = ForeignKeyField(model=Content)

    def to_json(self):
        return model_to_dict(self, exclude=get_exclude())


class Vote(db.db_wrapper.Model):
    target_id = IntegerField()
    target_type = IntegerField(
        choices=[(1, "user"), (2, "blog"), (3, "post"), (4, "comment")], default=3
    )
    voter = ForeignKeyField(model=User)
    vote_value = IntegerField()

    @classmethod
    def add_votes_info(cls, model_dict, type, user):
        model_dict["rating"] = (
            Vote.select(fn.SUM(Vote.vote_value).alias("rating"))
            .where(
                (Vote.target_id == model_dict["id"])
                & (Vote.target_type == type)  # noqa: E712
            )
            .first()
            .rating
            or 0
        )

        if user is not None:
            user_vote = Vote.get_or_none(
                (Vote.target_id == model_dict["id"])
                & (Vote.target_type == type)  # noqa: E712
                & (Vote.voter == user)  # noqa: E712
            )
            model_dict["user_voted"] = user_vote.vote_value if user_vote else 0
        else:
            model_dict["user_voted"] = 0

        return model_dict

    def to_json(self):
        return model_to_dict(self, exclude=get_exclude())


class Jam(db.db_wrapper.Model):
    creator = ForeignKeyField(model=User)
    blog = ForeignKeyField(model=Blog)
    title = TextField(null=True, default=None)
    url = CharField(null=True, unique=True)
    short_description = TextField(null=True, default=None)
    description = TextField(null=True, default=None)
    created_date = DateTimeField()
    start_date = DateTimeField(null=True, default=None)
    end_date = DateTimeField(null=True, default=None)
    logo = ForeignKeyField(model=Content, backref="logo", null=True)

    @classmethod
    def get_all_jams(cls):
        return cls.select().order_by(Jam.start_date.desc())

    def to_json(self):
        return model_to_dict(self, exclude=get_exclude())


class JamCriteria(db.db_wrapper.Model):
    jam = ForeignKeyField(model=Jam)
    title = TextField(null=True, default=None)


class JamEntry(db.db_wrapper.Model):
    creator = ForeignKeyField(model=User)
    short_info = TextField(null=True, default=None)
    info = TextField(null=True, default=None)
    created_date = DateTimeField()
    logo = ForeignKeyField(model=Content, backref="logo", null=True)

    def to_json(self):
        return model_to_dict(self, exclude=get_exclude())


class JamEntryPost(db.db_wrapper.Model):
    entry = ForeignKeyField(model=JamEntry)
    post = ForeignKeyField(model=Post)


class JamEntryVote(db.db_wrapper.Model):
    entry = ForeignKeyField(model=JamEntry)
    voter = ForeignKeyField(model=User)
    criteria = ForeignKeyField(model=JamCriteria)


class JamEntryFeedback(db.db_wrapper.Model):
    entry = ForeignKeyField(model=JamEntry)
    voter = ForeignKeyField(model=User)
    feedback = TextField()


class Achievement(db.db_wrapper.Model):
    title = TextField(null=True, default=None)
    image = ForeignKeyField(model=Content, backref="image", null=True)

    @classmethod
    def add_achievements(cls, user_dict):
        achievements = (
            Achievement.select(Achievement, AchievementUser.comment)
            .join(AchievementUser, JOIN.LEFT_OUTER)
            .where(AchievementUser.user == user_dict["id"])
        )

        json_achivements = []
        for a in achievements:
            _a = a.to_json()
            _a["comment"] = a.achievementuser.comment
            json_achivements.append(_a)

        user_dict["achievements"] = json_achivements

        return user_dict

    def to_json(self):
        return model_to_dict(self, exclude=get_exclude())


class AchievementUser(db.db_wrapper.Model):
    achievement = ForeignKeyField(model=Achievement)
    user = ForeignKeyField(model=User)
    comment = TextField(null=True, default=None)

    def to_json(self):
        return model_to_dict(self, exclude=get_exclude())
