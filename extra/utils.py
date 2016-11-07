from datetime import timedelta
from functools import update_wrapper
from flask import request, current_app, make_response
from datetime import datetime, date


class Serializer:
    __public__ = None

    def serialize(self, fieldset=None):
        res = {}
        if not self.__public__:
            self.__public__ = [m.key for m in self.__table__.columns]
        fields = self.__public__
        if fieldset and hasattr(self, '__fieldsets__'):
            fields = self.__fieldsets__.get(fieldset) or fields

        for public_key in fields:
            if isinstance(public_key, tuple):
                public_key, private_key = public_key
                value = getattr(self, private_key)
            else:
                value = getattr(self, public_key)

            if hasattr(value, '__iter__'):
                res[public_key] = list()
                for value_item in value:
                    if hasattr(value_item, 'serialize'):
                        res[public_key].append(value_item.serialize(fieldset))
                    else:
                        res[public_key].append(value_item)
            elif hasattr(value, 'serialize'):
                res[public_key] = value.serialize()
            elif isinstance(value, datetime):
                try:
                    res[public_key] = value.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    res[public_key] = ''
            elif isinstance(value, date):
                try:
                    res[public_key] = value.strftime('%Y-%m-%d')
                except ValueError:
                    res[public_key] = ''
            else:
                res[public_key] = value
        return res


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


def smart_trunc(text, width):
    if len(text) <= width:
        return text
    if text[width].isspace():
        text = text[0:width]
    else:
        text = text[0:width].rsplit(None, 1)[0]
    for delimiter in [",", ".", "!", "?", "/", "&", "-", ":", ";", "@", "'"]:
        text = text.strip(delimiter)
    return text + '...'


def format_sql(sql, params):
    for name, value in params.iteritems():
        sql = sql.replace(':'+name, str(value))
    return sql