from converters.models import TuVote, TuUser
from src import create_app
from src.model.models import Vote, User

create_app()

for v in TuVote.select():
    creator = User.get_or_none(User.id == v.user_voter)
    if not creator:
        print('Skipped vote. Owner:' +
              TuUser.get(TuUser.user == v.user).user_login)
        continue

    t_id = v.target
    t_type = 1
    if v.target_type == 'user':
        t_type = 1
    elif v.target_type == 'blog':
        t_type = 2
    elif v.target_type == 'topic':
        t_type = 3
    elif v.target_type == 'comment':
        t_type = 4

    value = 1 if v.vote_direction > 0 else -1

    Vote.create(
        target_id=t_id,
        target_type=t_type,
        voter=creator,
        vote_value=value,
        created_date=v.vote_date,
        updated_date=v.vote_date,
    )
