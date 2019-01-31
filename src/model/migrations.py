from peewee import Proxy, BooleanField, CharField
from playhouse.migrate import migrate, SchemaMigrator


def migration_v1(db, migrator: SchemaMigrator):
    from src.model.models import Post

    if hasattr(Post, 'has_cut'):
        return

    with db.atomic():
        migrate(
            migrator.add_column('post', 'has_cut',
                                BooleanField(default=False)),
            migrator.add_column('post', 'cut_name',
                                CharField(default=None, null=True)),
        )

    query = Post.select()

    for p in query:
        p.has_cut = '<cut>' in p.text
        p.save()


migrations = [
    migration_v1
]


def migrate_schema(db):
    from src.model.models import DatabaseInfo

    if isinstance(db, Proxy):
        db = db.obj

    migrator = SchemaMigrator.from_database(db)

    if migrator is None:
        print(db)
        raise Exception('Migrator is broken')

    info = DatabaseInfo.get_or_none(id=0)
    if info is None:
        info = DatabaseInfo.create(id=0, version=0)

    for i in range(info.version, len(migrations)):
        migrations[i](db, migrator)

        info.version = i + 1
        info.save()
