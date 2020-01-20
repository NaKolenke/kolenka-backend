from converters.models import TuTopic, TuUser, TuTopicContent
from src import create_app
from converters import content
from src.model.models import Post, Blog, User, Tag, TagMark

create_app()

# <cut></p> -> </p><cut/>
# <cut></div> -> </div><cut/> span
# <alto:spoiler> -> spoiler
# <alto:user login="pevzi" style="pointer-events: none; border: 1px dotted #3A3A3A; background: #d5d5d5; display: inline;">pevzi</alto:user>
# <alto:spoiler style="border: 1px dotted #3A3A3A; background: #d5d5d5; display: block;" title="Спойлер">
# </alto:spoiler>
# Стикеры


for t in TuTopic.select():
    creator = User.get_or_none(User.id == t.user)
    if not creator:
        print('Skipped post. Owner:' +
              TuUser.get(TuUser.user == t.user).user_login)
        continue

    updated = t.topic_date_edit
    if not updated:
        updated = t.topic_date_add

    topic_content = TuTopicContent.get(TuTopicContent.topic == t.topic)
    text = topic_content.topic_text_source

    text = content.replace_uploads_in_text(creator, text)
    # TODO convert questions and photosets

    cut = text.split('<cut>')[0]
    post = Post.create(
        id=t.topic,
        blog=Blog.get(Blog.id == t.blog),
        creator=creator,
        created_date=t.topic_date_add,
        updated_date=updated,
        title=t.topic_title,
        cut_text=cut,
        has_cut='<cut>' in text,
        text=text,
        rating=0,
        is_draft=t.topic_publish == 0,
        is_on_main=t.topic_publish_index == 1,
        reads=0,
        url=t.topic_url,
    )

    tags = t.topic_tags.split(',')
    for tag in tags:
        tag_obj = Tag.get_or_none(title=tag)
        if tag_obj is None:
            tag_obj = Tag.create(title=tag, created_date=t.topic_date_add)
        TagMark.create(tag=tag_obj, post=post)
