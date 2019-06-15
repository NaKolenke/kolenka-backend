from datetime import date, datetime, timezone
import bleach
from flask.json import JSONEncoder

allowed_tags = bleach.ALLOWED_TAGS + \
    ['div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'u', 's', 'hr',
     'table', 'tbody', 'tr', 'td', 'th']

allowed_attrs = dict(bleach.ALLOWED_ATTRIBUTES)
allowed_attrs.update({'*': ['data', 'style']})

allowed_styles = ['color', 'text-align']


def sanitize(html):
    if not html:
        return html

    ret = bleach.clean(
        html,
        allowed_tags,
        allowed_attrs,
        allowed_styles,
        strip=True)
    ret = bleach.linkify(ret)
    return ret


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
