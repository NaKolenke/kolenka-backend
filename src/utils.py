from datetime import date, datetime, timezone

from flask.json import JSONEncoder


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
