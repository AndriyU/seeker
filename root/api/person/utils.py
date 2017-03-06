from operator import itemgetter
from pprint import pprint
from extra.geo_utils import get_address_details
from extra import db
from extra.models.specialty import SpecialtyInfo
from extra.models.address import Address


def print_sql(sql, sql_params):
    for key, value in sql_params.iteritems():
        if isinstance(value, basestring):
            value = "'%s'" % (value, )
        else:
            value = str(value)
        sql = sql.replace(':'+str(key), value)
    print sql
