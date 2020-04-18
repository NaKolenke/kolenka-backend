import re
from src import create_app
from src.model.models import Post, Comment


def process_text(text):
    # replace video tag:
    # <video>https://www.youtube.com/watch?v=jQOJ3yCK8pI</video>
    # <video width="300" height="150">https://www.youtube.com/watch?v=miq0y75ObY4</video>
    # to iframe
    # <iframe width="700" height="393,9223410242" src="http://www.youtube.com/embed/miq0y75ObY4" frameborder="0" webkitAllowFullScreen mozallowfullscreen allowfullscreen="allowfullscreen"></iframe>
    text = text.replace("http://www.youtube.com", "https://www.youtube.com")
    text = text.replace("http://youtube.com", "https://youtube.com")

    video_re = r"\<video(.*?)?http(s?):\/\/(www.)?youtube.com/watch\?v=([a-zA-Z0-9-_].*?)\s*\<\/video\>"

    def video_repl(m):
        video_id = m.group(4)

        return f'<iframe src="https://www.youtube.com/embed/{video_id}" frameborder="0" webkitAllowFullScreen mozallowfullscreen allowfullscreen="allowfullscreen"></iframe>'

    text = re.sub(video_re, video_repl, text)

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
