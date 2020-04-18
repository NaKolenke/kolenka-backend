from src import create_app
from src.model.models import Post, Comment

# &nbsp -> space


def process_text(text):
    text = text.replace("&nbsp", " ")

    return text


def convert():
    create_app()

    for p in Post.select():
        if not p.text:
            continue
        p.text = process_text(p.text)
        p.save()

    for c in Comment.select():
        if not c.text:
            continue
        c.text = process_text(c.text)
        c.save()
