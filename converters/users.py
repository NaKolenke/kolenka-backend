import datetime
from converters.models import TuUser, TuSession, TuMresource
from converters import content
from src import create_app
from src.model.models import User

create_app()

removed = 0
for u in TuUser.select():
    was_removed = False
    if u.user_activate == 0 and not u.user_last_session:
        was_removed = True

    has_session_in_one_day = True

    s = TuSession.get_or_none(TuSession.session_key == u.user_last_session)
    if s:
        if (s.session_date_last - u.user_date_register).days > 0.5:
            has_session_in_one_day = False

    if has_session_in_one_day:
        was_removed = True

    last_session_date = datetime.datetime(year=1970, month=1, day=1)
    for s in TuSession.select().where(TuSession.user == u.user):
        if s.session_date_last > last_session_date:
            last_session_date = s.session_date_last

    if was_removed:
        removed = removed + 1
    else:
        year = u.user_date_register.year
        month = u.user_date_register.month
        avatar = content.create_content(
            u.user_profile_avatar,
            'profile_avatar',
            u.user,
            u.user,
            year,
            month)

        user = User.create(
            id=u.user,
            login=u.user_login,
            password=u.user_password,
            email=u.user_mail,
            registration_date=u.user_date_register,
            last_active_date=last_session_date,
            name=u.user_profile_name,
            birthday=u.user_profile_birthday,
            about=None,
            avatar=avatar,
            is_admin=u.user_role > 1
        )

        about = content.replace_uploads_in_text(user, u.user_profile_about)
        user.about = about
        user.save()

force_created_users = [
    5, 8, 21, 62, 97, 382, 44, 3392, 3412, 3425, 3398, 416,
    383, 150, 337, 378, 398, 3427, 3434, 88]

for id in force_created_users:
    if User.get_or_none(User.id == id):
        continue

    u = TuUser.get(TuUser.user == id)

    year = u.user_date_register.year
    month = u.user_date_register.month
    avatar = content.create_content(
        u.user_profile_avatar,
        'profile_avatar',
        u.user,
        u.user,
        year,
        month)

    User.create(
        id=u.user,
        login=u.user_login,
        password=u.user_password,
        email=u.user_mail,
        registration_date=u.user_date_register,
        last_active_date=last_session_date,
        name=u.user_profile_name,
        birthday=u.user_profile_birthday,
        about=u.user_profile_about,
        avatar=avatar,
        is_admin=u.user_role > 1
    )

print('Removed %d users' % removed)
