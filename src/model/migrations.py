import os

from peewee import (
    BigIntegerField,
    BooleanField,
    CharField,
    ForeignKeyField,
    IntegerField,
    Proxy,
    TextField,
)
from playhouse.migrate import SchemaMigrator, migrate


def migration_v1(db, migrator: SchemaMigrator):
    from src.model.models import Post

    with db.atomic():
        migrate(
            migrator.add_column("post", "has_cut", BooleanField(default=False)),
            migrator.add_column("post", "cut_name", CharField(default=None, null=True)),
        )

    query = Post.select()

    for p in query:
        p.has_cut = "<cut>" in p.text
        p.save()


def migration_v2(db, migrator: SchemaMigrator):
    with db.atomic():
        migrate(migrator.rename_column("user", "login", "username"),)


def migration_v3(db, migrator: SchemaMigrator):
    import magic

    from src.model.models import Content

    with db.atomic():
        migrate(
            migrator.add_column("content", "mime", CharField(default="")),
            migrator.add_column("content", "size", BigIntegerField(default=0)),
        )
    query = Content.select()

    for c in query:
        c.mime = magic.from_file(c.path, mime=True)
        c.size = os.stat(c.path).st_size
        c.save()


def migration_v4(db, migrator: SchemaMigrator):
    from src.model.models import Token

    with db.atomic():
        migrate(migrator.add_column("token", "token_type", CharField(default="")),)

    query = Token.select()
    for t in query:
        if t.is_refresh_token:
            t.token_type = "refresh"
        else:
            t.token_type = "access"
        t.save()


def migration_v5(db, migrator: SchemaMigrator):
    with db.atomic():
        migrate(
            migrator.drop_column("post", "rating"),
            migrator.drop_column("comment", "rating"),
        )


def migration_v6(db, migrator: SchemaMigrator):
    with db.atomic():
        migrate(
            migrator.drop_column("jam", "short_description"),
            migrator.add_column("jamcriteria", "order", IntegerField(default=0)),
        )


def migration_v7(db, migrator: SchemaMigrator):
    with db.atomic():
        migrate(migrator.add_column("jam", "status", IntegerField(default=0)),)


def migration_v8(db, migrator: SchemaMigrator):
    with db.atomic():
        migrate(
            migrator.add_column(
                "jam", "short_description", TextField(null=True, default=None)
            ),
        )


def migration_v9(db, migrator: SchemaMigrator):
    from src.model.models import Jam

    with db.atomic():
        migrate(
            migrator.add_column(
                "jamentry",
                "jam_id",
                ForeignKeyField(Jam, Jam.id, default=None, null=True, index=False),
            ),
        )


def migration_v10(db, migrator: SchemaMigrator):
    with db.atomic():
        migrate(
            migrator.add_column(
                "jamentry", "title", TextField(null=True, default=None)
            ),
            migrator.add_column("jamentry", "url", CharField(null=True)),
        )


def migration_v11(db, migrator: SchemaMigrator):
    with db.atomic():
        migrate(migrator.add_column("jamentrylink", "order", IntegerField(default=0)),)


def migration_v12(db, migrator: SchemaMigrator):
    with db.atomic():
        migrate(
            migrator.add_column("jamentry", "is_archived", BooleanField(default=False)),
        )


def migration_v13(db, migrator: SchemaMigrator):
    with db.atomic():
        migrate(
            migrator.add_column("comment", "object_type", CharField(null=True)),
            migrator.add_column("comment", "object_id", IntegerField(default=0)),
        )

        from src.model.models import Comment

        for c in Comment.select():
            c.object_type = "post"
            c.object_id = c.post.id
            c.save()

        migrate(
            # migrator.drop_foreign_key_constraint("comment", "post"),
            migrator.drop_column("comment", "post_id"),
        )


def migration_v14(db, migrator: SchemaMigrator):
    with db.atomic():
        migrate(migrator.add_column("jamentryvote", "vote", IntegerField(default=0)))


migrations = [
    migration_v1,
    migration_v2,
    migration_v3,
    migration_v4,
    migration_v5,
    migration_v6,
    migration_v7,
    migration_v8,
    migration_v9,
    migration_v10,
    migration_v11,
    migration_v12,
    migration_v13,
    migration_v14,
]


def migrate_schema(db):
    print("Starting migration")

    from src.model.models import DatabaseInfo

    if isinstance(db, Proxy):
        db = db.obj

    migrator = SchemaMigrator.from_database(db)

    if migrator is None:
        raise Exception("Migrator is broken")

    info = DatabaseInfo.get_or_none(id=0)
    if info is None:
        info = DatabaseInfo.create(id=0, version=0)

    print("Current database version is %d" % info.version)

    for i in range(info.version, len(migrations)):
        print(f"Applying migration v{i+1}")

        migrations[i](db, migrator)

        info.version = i + 1
        info.save()
