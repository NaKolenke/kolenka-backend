from src import create_app
from src.model.models import Content


def convert():
    create_app()

    print("Replacing content")

    for c in Content.select():
        c.path = c.path.replace(
            "/home/service/kolenka-backend/", "/home/service/kolenka-beta-backend/"
        )
        print("New path " + c.path)
        c.save()
