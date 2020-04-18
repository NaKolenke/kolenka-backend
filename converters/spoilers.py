import re
from src import create_app
from src.model.models import Post, Comment

# <alto:spoiler> -> spoiler
# <alto:spoiler style="border: 1px dotted #3A3A3A; background: #d5d5d5; display: block;" title="Спойлер">
# </alto:spoiler>


def process_text(text):
    spoiler_re = r"\<alto\:spoiler(.*?)>((.|[\r\n])*?)\<\/alto\:spoiler\>"
    title_re = r"title=\"(.*?)\""

    def spoiler_repl(m):
        attrs_str = m.group(1)
        title_match = re.search(title_re, attrs_str)
        title = None
        if title_match:
            title = title_match.group(1)

        content = m.group(2)
        if title:
            return f'<spoiler title="{title}">{content}</spoiler>'
        else:
            return f"<spoiler>{content}</spoiler>"

    text = re.sub(spoiler_re, spoiler_repl, text, flags=re.MULTILINE)

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
