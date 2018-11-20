import datetime
from converters.models import TuUser, TuSession
from src import create_app
from src.model.user import User

create_app()

removed = 0
for u in TuUser.select():
    was_removed = False
    if u.user_activate == 0 and not u.user_last_session:
        was_removed = True

    has_session_in_one_day = True
    
    for s in TuSession.select().where(TuSession.user == u.user):
        if (s.session_date_last - u.user_date_register).days > 1:
            has_session_in_one_day = False
            break
    if has_session_in_one_day:
        was_removed = True
    
    last_session_date = datetime.datetime(year=1970, month=1, day=1)
    for s in TuSession.select().where(TuSession.user == u.user):
        if s.session_date_last > last_session_date:
            last_session_date = s.session_date_last
    
    if was_removed:
        removed = removed + 1
    else:
        User.create(
            id = u.user,
            login=u.user_login,
            password=u.user_password,
            email=u.user_mail,
            registration_date=u.user_date_register,
            last_active_date=last_session_date,
            name=u.user_profile_name,
            birthday=u.user_profile_birthday,
            about=u.user_profile_about,
            avatar=u.user_profile_avatar
        )


print('Removed %d users' % removed)