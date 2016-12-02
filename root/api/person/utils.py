from operator import itemgetter
from pprint import pprint
from extra.geo_utils import get_address_details
from extra import db
from extra.models.specialty import SpecialtyDetails
from extra.models.address import Address


SQL = """SELECT npi, 
                min(st_distance(Geography(ST_MakePoint(longitude, latitude)),
                        Geography(ST_MakePoint(:longitude, :latitude)))) as distance,
                ARRAY_AGG(address_checksum) as addresses_checksum,
                ARRAY_AGG(st_distance(Geography(ST_MakePoint(longitude, latitude)),
                        Geography(ST_MakePoint(:longitude, :latitude)))) as distances,
                first(accepts_new_patients),
                max(gender),
                first(is_pcp) as is_pcp,
                first(title) AS title,
                first(specialty_groups)
                FROM rover.doctor_filtered_address
         WHERE 
             ST_DWithin(Geography(ST_MakePoint(longitude, latitude)),
                        Geography(ST_MakePoint(:longitude, :latitude)),
                        :radius * 1609.34)
             AND {where}
         GROUP BY npi
         ORDER BY distance
         LIMIT :limit
         OFFSET :offset"""


def print_sql(sql, sql_params):
    for key, value in sql_params.iteritems():
        if isinstance(value, basestring):
            value = "'%s'" % (value, )
        else:
            value = str(value)
        sql = sql.replace(':'+str(key), value)
    print sql
