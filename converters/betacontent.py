from src import create_app
from src.model.models import Content

create_app()

for c in Content.select():
    c.path = c.path.replace(
        '/home/service/kolenka-backend/',
        '/home/service/kolenka-beta-backend/')
    c.save()
