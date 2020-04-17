import re
from src import create_app
from src.model.models import Post

create_app()

for p in Post.select():
    p.text = p.text.replace("http://www.youtube.com", "https://www.youtube.com")
    p.text = p.text.replace("http://youtube.com", "https://youtube.com")

    video_re = r"\<video(.*?)?http(s?):\/\/(www.)?youtube.com/watch\?v=([a-zA-Z0-9-_].*?)\s*\<\/video\>"

    def video_repl(m):
        video_id = m.group(4)

        return f'<iframe src="https://www.youtube.com/embed/{video_id}" frameborder="0" webkitAllowFullScreen mozallowfullscreen allowfullscreen="allowfullscreen"></iframe>'

    p.text = re.sub(video_re, video_repl, p.text)
    # <video>https://www.youtube.com/watch?v=jQOJ3yCK8pI</video>
    # <video width="300" height="150">https://www.youtube.com/watch?v=miq0y75ObY4</video>
    # <iframe width="700" height="393,9223410242" src="http://www.youtube.com/embed/miq0y75ObY4" frameborder="0" webkitAllowFullScreen mozallowfullscreen allowfullscreen="allowfullscreen"></iframe>
    p.save()
