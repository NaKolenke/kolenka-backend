import sys
from src.model.migrations import migrate_schema

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(
            """Specify argument.
Possible commands:
migrate
convert users
convert blogs
For launching flask server see README.md"""
        )
    elif sys.argv[1] == "migrate":
        from src import create_app
        from src.model import db

        create_app()

        migrate_schema(db.get_database())
    elif sys.argv[1] == "convert":
        if len(sys.argv) == 3:
            from converters import convert

            convert(sys.argv[2])
        else:
            print("Use convert <type>")
    else:
        print("Unrecognized command")
