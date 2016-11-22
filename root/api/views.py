# -*- coding: utf-8 -*-
from pprint import pprint, pformat
from cStringIO import StringIO
from webargs.flaskparser import use_kwargs
from flask import Blueprint, current_app as ca
from .utils import return_response, log
from extra import db
from extra.geo_utils import get_address_details
from root import fields

api = Blueprint('api', __name__, url_prefix='/v1.0')

from person.views import *
from specialty.views import *


@api.route('/system_ping/')
def system_ping():
    try:
        msg = "Flask: ok."
        res = db.session.execute("SELECT")
        if len(list(res)) != 1:
            log('Database problem', 'fatal')
            return str('Database problem'), 503
        msg += ' DB: ok.'
        return msg, 200
    except Exception, e:
        log(e, 'fatal')
        return "%s: %s" % ("Database problem", str(e)), 503


@api.route('/test', methods=['GET'])
def test():

    return return_response({'freds': 'test'}, status=200)


@api.route('/get_address_details/')
# @cache.memoize_considering_request()
@use_kwargs({
    'city': fields.city,
    'state': fields.state,
    'county': fields.county,
    'zip_code': fields.zip_code,
    'one_zip': fields.true_false,
})
def gad(**address):
    if not address['city'] and not address['state'] and not address['county'] and not address['zip_code']:
        return return_response([])

    ret = get_address_details(address)
    return return_response(ret)