import time
import re
from pprint import pprint
from webargs.flaskparser import use_kwargs

from ..views import api
from root import fields
from extra import db
from extra.geo_utils import get_coordinates
from extra.models.organization import Organization
from extra.models.address import Address, GeoAddressDetails
from sqlalchemy import func
from root.api.utils import return_response, log, elapsed_time, split_int_ids


distance_select = '''round(cast(min(st_distance(Geography(ST_MakePoint(a.longitude, a.latitude)),
                  Geography(ST_MakePoint(:longitude, :latitude)))/1609.34) as numeric), 2)'''
distance_calc = '''AND ST_DWithin(Geography(ST_MakePoint(longitude, latitude)),
                Geography(ST_MakePoint(:longitude, :latitude)),
                :radius * 1609.34)'''

SQL = """SELECT o.uid, o.uid_type, o.url_path,
                {distance_select} as distance,
                min(a.checksum) as address_checksum,
                o.name as name,
                o.other_name as other_name,
                o.short_name as short_name,
                o.types as types
                FROM public.organization as o
                JOIN public.address as a ON o.uid = a.resident_uid
         WHERE
             o.active = true AND a.practice = true
             {where}
             {distance_calc}
         GROUP BY o.uid
         ORDER BY distance
         LIMIT :limit
         OFFSET :offset"""
@api.route('/organization/search/')
# @cache.memoize_considering_request()
@use_kwargs({
    'uid': fields.request_int,
    'uid_type': fields.request_string,
    'name': fields.request_string,
    'url_path': fields.request_string,
    'radius': fields.radius,
    'latitude': fields.latitude,
    'longitude': fields.longitude,
    'zip_code': fields.zip_code,
    'state': fields.state,
    'city': fields.city,
    'limit': fields.limit,
    'page': fields.page,
})
def organization_search(uid, uid_type, name, url_path, radius, latitude, longitude,
                    zip_code, state, city, limit, page):
    start_time = time.time()

    latitude, longitude = get_coordinates(latitude,
                                       longitude,
                                       zip_code,
                                       city,
                                       state)
    where = []
    sql_params = {'limit': limit,
                  'offset': (page - 1) * limit}

    if uid is not None:
        sql_params['uid'] = uid
        where.append("o.uid=:uid")
    if url_path is not None:
        sql_params['url_path'] = url_path
        where.append("o.url_path=:url_path")
    if name is not None:
        sql_params['name'] = "%{name}%".format(name=name)
        where.append("(o.name=:name OR o.other_name=:name OR o.short_name=:name)")
    if radius and latitude and longitude:
        sql_params['latitude'] = latitude
        sql_params['longitude'] = longitude
        sql_params['radius'] = radius
        ds = distance_select
        dc = distance_calc
    else:
        if zip_code is not None:
            sql_params['zip_code'] = zip_code
            where.append("a.zip_code=:zip_code")
        if city is not None:
            sql_params['city'] = city
            where.append("a.city=:city")
        if state is not None:
            sql_params['state'] = state
            where.append("a.state=:state")

        ds = '0'
        dc = ''

    if where:
        where = "AND %s" % ' AND '.join(where)
    else:
        where = ''

    sql = SQL.format(distance_select=ds,
                     distance_calc=dc,
                     where=where)
    cursor = db.session.execute(sql, sql_params)

    elapsed_time(start_time, 'Pharmacy Search END')
    results = []
    for row in cursor:
        p = dict(row)
        address = Address.query.get_or_404(p['address_checksum']).serialize()
        p['address'] = address
        del p['address_checksum']
        results.append(p)
    elapsed_time(start_time, 'Added addresses END')

    return return_response(results)


@api.route('/organization/')
# @cache.memoize_considering_request()
@use_kwargs({
    'uid': fields.request_int,
    'url_path': fields.request_string})
def organization_details(uid, url_path):
    if not uid and not url_path:
        return return_response({'error': 'uid or url_path are required!'}, 412)

    if uid:
        organization = Organization.query.get_or_404(uid)
    else:
        organization = db.session.query(Organization).filter(Organization.url_path == url_path).first()

    return return_response(organization.serialize())


@api.route('/pharmacy/batch/')
# @cache.memoize_considering_request()
@use_kwargs({'uids': fields.request_int_required})
def organization_details_batch(uids):
    uid_list = split_int_ids(uids)

    organisations = Organization.query.filter(Organization.uid.in_(uid_list))
    return return_response([o.serialize() for o in organisations if o])


@api.route('/pharmacy/count/<any(state, county, city, zip_code):group_by>/')
# @cache.memoize_considering_request()
@use_kwargs({
    'type': fields.request_string,
    'state': fields.state,
    'county': fields.county,
    'city': fields.city,
    'zip_code': fields.zip_code,
})
def pharmacy_count(group_by, type, state, county, city, zip_code):
    if group_by == 'county':
        group_field = GeoAddressDetails.county_name
    elif group_by == 'zip_code':
        group_field = Address.zip_code
        group_by = 'zip_code'
    else:
        group_field = getattr(Address, group_by)

    query = db.session.query(func.count(Pharmacy.npi.distinct()), group_field). \
        join(Address, Pharmacy.npi == Address.npi)
    if group_by == 'county' or county:
        query = query.join(GeoAddressDetails, GeoAddressDetails.zip_code == Address.zip_code)

    if state:
        query = query.filter(Address.state.ilike(state))
    if county:
        query = query.filter(GeoAddressDetails.county_name.ilike(re.sub('[-\s]', '_', county)))
    if city:
        query = query.filter(Address.city.ilike(re.sub('[-\s]', '_', city)))
    if zip_code:
        query = query.filter(Address.zip_code==zip_code)
    if type and type != 'all':
        if type == 'other':
            query = query.filter(Organization.type.is_(None))
        else:
            query = query.filter(Organization.types == type)  # TODO rework as array search

    query = query.group_by(group_field).order_by(group_field)

    return return_response({n[1]: n[0] for n in query.all()})




