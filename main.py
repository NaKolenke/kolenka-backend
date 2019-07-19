import sys
from src.model.migrations import migrate_schema

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('''Specify argument.
Possible commands:
migrate
convert users
convert blogs
For launching flask server see README.md''')
    elif sys.argv[1] == 'migrate':
        from src import create_app
        from src.model import db

        create_app()

        migrate_schema(db.get_database())
    elif sys.argv[1] == 'convert':
        if len(sys.argv) == 2:
            print('Converting all models')
            print('Converting users')
            import converters.users

            print('Converting blogs')
            import converters.blogs

            print('Converting posts')
            import converters.posts

            print('Converting comments')
            import converters.comments
        elif len(sys.argv) == 3:
            if sys.argv[2] == 'users':
                import converters.users
            elif sys.argv[2] == 'blogs':
                import converters.blogs
            elif sys.argv[2] == 'posts':
                import converters.posts
            elif sys.argv[2] == 'comments':
                import converters.comments
            elif sys.argv[2] == 'betacontent':
                import converters.betacontent
            elif sys.argv[2] == 'stickers':
                import converters.stickers
        else:
            print('Unrecognized command')
