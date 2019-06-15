import datetime
from converters.models import TuBlog, TuBlogUser, TuUser
from src import create_app
from converters import content
from src.model.models import Blog, User, BlogParticipiation

create_app()


def get_blog_type(blog):
    if blog.blog_type == 'open':
        return 1
    elif blog.blog_type == 'hidden':
        return 3
    else:
        return 2


for b in TuBlog.select():
    blog_type = get_blog_type(b)

    year = b.blog_date_add.year
    month = b.blog_date_add.month
    avatar = content.create_content(b.blog_avatar, 'blog_avatar', b.blog, b.user_owner, year, month)

    updated = b.blog_date_edit
    if not updated:
        updated = b.blog_date_add

    owner = User.get_or_none(User.id == b.user_owner)
    if not owner:
        print('Skipped blog. Owner:' + TuUser.get(TuUser.user == b.user_owner).user_login)
        continue

    about = content.replace_uploads_in_text(owner, b.blog_description)

    url = b.blog_url or 'blog' + str(b.blog)
    blog = Blog.create(
        id=b.blog,
        created_date=b.blog_date_add,
        updated_date=updated,
        description=about,
        title=b.blog_title,
        url=url,
        blog_type=blog_type,
        creator=owner,
        image=avatar
    )

    BlogParticipiation.create(
        blog=blog,
        user=owner,
        role=1,
    )

for bu in TuBlogUser.select():
    role = 1
    if bu.user_role == 1:
        role = 3
    if bu.user_role > 1:
        role = 1

    BlogParticipiation.create(
        blog=Blog.get(Blog.id == bu.blog),
        user=User.get(User.id == bu.user),
        role=role,
    )
