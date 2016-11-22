import re
import time
import crcmod
from decimal import Decimal
from pprint import pformat
from datetime import datetime, date
from flask import request, current_app as ca, json, Response
from extra.utils import crossdomain

protocol_re = re.compile(r'^http://|^https://')
split_re = re.compile(';|,')
crc64_unsigned = crcmod.predefined.mkPredefinedCrcFun('crc64')


def crc64(data):
    return crc64_unsigned(data) - 0xffffffffffffffff/2


def capitalize(title):
    return ' '.join([
        word.capitalize() if word not in
                             ('and', 'or', 'on', 'for', 'of', 'the', 'a', 'an', 'at') or
                             idx == 0 else word
        for idx, word in enumerate(title.split(' '))
    ])


def fix_url(url_str):
    if url_str and not protocol_re.match(url_str):
        url_str = "http://%s" % url_str

    return url_str


def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    if isinstance(obj, datetime):
        return obj.strftime('%m/%d/%Y %H:%M')
    if isinstance(obj, date):
        return obj.strftime('%m/%d/%Y')
    if isinstance(obj, Decimal):
        return float(obj)
    return obj


# @crossdomain(origin='*')
def return_response(response_obj, status=200):
    return Response(json.dumps(response_obj, default=set_default),
                    content_type='application/json', status=status)


def elapsed_time(start_time, msg=''):
    log("%s: %s\n" % (msg, time.time() - start_time))


def log(message, level='info'):
    log_levels = {
        'debug': ca.logger.debug,  # 10
        'info': ca.logger.info,  # 20
        'warn': ca.logger.warning,  # 30
        'error': ca.logger.error,  # 40
        'fatal': ca.logger.fatal,  # 50
    }
    if type(message) in [list, dict, tuple]:
        log_levels[level](pformat(message))
    else:
        log_levels[level](message)


def is_digit(x):
    try:
        int(x)
        return True
    except ValueError:
        return False


def split_int_ids(ids):
    if ids:
        return set(int(num.strip()) for num in split_re.split(ids) if is_digit(num.strip()))  # (prevent duplicates)
