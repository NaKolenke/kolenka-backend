import os
from peewee import Proxy, BooleanField, CharField, BigIntegerField
from playhouse.migrate import migrate, SchemaMigrator


def migration_v1(db, migrator: SchemaMigrator):
    print('Applying migration v1')

    from src.model.models import Post

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


def migration_v2(db, migrator: SchemaMigrator):
    print('Applying migration v2')

    with db.atomic():
        migrate(
            migrator.rename_column('user', 'login', 'username'),
        )


def migration_v3(db, migrator: SchemaMigrator):
    print('Applying migration v3')

    import magic
    from src.model.models import Content

    with db.atomic():
        migrate(
            migrator.add_column('content', 'mime',
                                CharField(default="")),
            migrator.add_column('content', 'size',
                                BigIntegerField(default=0)),
        )
    query = Content.select()

    for c in query:
        c.mime = magic.from_file(c.path, mime=True)
        c.size = os.stat(c.path).st_size
        c.save()


migrations = [
    migration_v1,
    migration_v2,
    migration_v3,
]


def migrate_schema(db):
    print('Starting migration')

    from src.model.models import DatabaseInfo

    if isinstance(db, Proxy):
        db = db.obj

    migrator = SchemaMigrator.from_database(db)

    if migrator is None:
        raise Exception('Migrator is broken')

    info = DatabaseInfo.get_or_none(id=0)
    if info is None:
        info = DatabaseInfo.create(id=0, version=0)

    print('Current database version is %d' % info.version)

    for i in range(info.version, len(migrations)):
        migrations[i](db, migrator)

        info.version = i + 1
        info.save()
