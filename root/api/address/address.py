import time
import re
from pprint import pprint
from webargs.flaskparser import use_kwargs

from ..views import api
from root import fields
from extra import db
from extra.models.address import Address, GeoAddressDetails
from sqlalchemy import func
from root.api.utils import return_response, log, elapsed_time, split_int_ids



@api.route('/address/')
@use_kwargs({'aid': fields.request_int})
def address(aid):
    address = Address.query.get_or_404(aid)
    return return_response(address.serialize())


@api.route('/address/batch/')
@use_kwargs({'aid': fields.request_int})
def address_batch(aid):
    aid_list = split_int_ids(aid)
    addresses = Address.query.filter(Address.id.in_(aid_list))
    return return_response([addr.serialize() for addr in addresses if addr])

