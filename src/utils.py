import functools
from datetime import date, datetime, timezone
import bleach
from bleach.linkifier import Linker
from flask.json import JSONEncoder

allowed_tags = bleach.ALLOWED_TAGS + [
    "div",
    "span",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "p",
    "u",
    "s",
    "hr",
    "table",
    "tbody",
    "tr",
    "td",
    "th",
    "img",
    "pre",
    "sup",
    "sub",
    "del",
    "br",
    "iframe",
    "cut",
]

allowed_attrs = dict(bleach.ALLOWED_ATTRIBUTES)
allowed_attrs.update(
    {
        "*": ["data", "style"],
        "img": ["src", "width", "height", "alt", "title"],
        "iframe": ["src", "allowfullscreen", "frameborder", "width", "height"],
        "cut": ["name"],
    }
)

allowed_styles = ["color", "text-align", "visibility"]


def sanitize(html):
    if not html:
        return html

    ret = bleach.clean(
        html,
        tags=allowed_tags,
        attributes=allowed_attrs,
        styles=allowed_styles,
        strip=True,
    )
    linker = Linker(recognized_tags=allowed_tags)
    ret = linker.linkify(ret)
    return ret


def doc_sample(body=None, response=None):
    def func_wrapper(fn):
        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            return fn(*args, **kwargs)

        wrapped.sample_body = body
        wrapped.sample_response = response
        return wrapped

    return func_wrapper


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                millis = int(obj.replace(tzinfo=timezone.utc).timestamp())
                return millis
            if isinstance(obj, date):
                millis = int(obj.replace(tzinfo=timezone.utc).timestamp())
                return millis
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)
