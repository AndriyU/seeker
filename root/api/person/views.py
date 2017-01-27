import time
import re
from pprint import pprint
from flask import current_app as ca
from webargs.flaskparser import use_kwargs
from sqlalchemy import func, or_, and_, desc
from ..views import api
from extra.geo_utils import get_coordinates
from ..utils import return_response, elapsed_time, split_int_ids, split_re, capitalize
from root import fields
from extra.models.person import Person, MyService, MySpecialty
from extra import db


distance_select = '''round(cast(min(st_distance(Geography(ST_MakePoint(a.longitude, a.latitude)),
                  Geography(ST_MakePoint(:longitude, :latitude)))/1609.34) as numeric), 2)'''
distance_calc = '''AND ST_DWithin(Geography(ST_MakePoint(longitude, latitude)),
                Geography(ST_MakePoint(:longitude, :latitude)),
                :radius * 1609.34)'''

SQL = """SELECT p.uid, p.uid_type, p.url_path, p.title, p.gender,
                {distance_select} as distance,
                min(a.checksum) as addresses_checksum
                FROM public.person as p
                JOIN public.address as a ON p.id = a.person_uid
         WHERE {where}
             {distance_calc}
         GROUP BY p.id
         ORDER BY distance
         LIMIT :limit
         OFFSET :offset"""


@api.route('/person/search/')
# @cache.memoize_considering_request()
@use_kwargs({
    'uid': fields.request_int,
    'title': fields.request_string,
    'url_path': fields.request_string,
    'gender': fields.gender_short,
    'specialty_code': fields.request_int,
    'specialty_url_path': fields.request_string,
    'radius': fields.radius,
    'latitude': fields.latitude,
    'longitude': fields.longitude,
    'zip_code': fields.zip_code,
    'state': fields.state,
    'city': fields.city,
    'limit': fields.limit,
    'page': fields.page,
})
def person_search(uid, title, url_path, gender, specialty_code, specialty_url_path,
                  radius, latitude, longitude, zip_code, state, city, limit, page):
    start_time = time.time()

    latitude, longitude = get_coordinates(latitude,
                                       longitude,
                                       zip_code,
                                       city,
                                       state)
    where = []
    sql_params = {'limit': limit,
                  'offset': (page - 1) * limit}

    if title is not None:
        sql_params['title'] = "%{}%".format(title)
        where.append("p.title ILIKE :title")
    if uid is not None:
        sql_params['uid'] = uid
        where.append("p.uid=:uid")
    if url_path is not None:
        sql_params['url_path'] = url_path
        where.append("p.url_path=:url_path")
    if gender is not None:
        sql_params['gender'] = gender
        where.append("p.gender=:gender")
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
        where = "%s" % ' AND '.join(where)
    else:
        where = ''

    sql = SQL.format(distance_select=ds,
                     distance_calc=dc,
                     where=where)
    ca.logger.info(sql)
    cursor = db.session.execute(sql, sql_params)

    results = []
    for row in cursor:
        results.append(dict(row))
    return return_response(results)


@api.route('/person/')
# @cache.memoize_considering_request()
@use_kwargs({
    'uid': fields.request_int,
    'url_path': fields.request_string})
def person_details(uid, url_path):
    if not uid and not url_path:
        return return_response({'error': 'uid or url_path are required!'}, 412)

    if uid:
        person = Person.query.get_or_404(uid)
    else:
        person = db.session.query(Person).filter(Person.url_path == url_path).first()

    return return_response(person.serialize())


@api.route('/person/batch/')
# @cache.memoize_considering_request()
@use_kwargs({'iuds': fields.request_int_list})
def person_info_batch(iuds):
    iud_list = split_int_ids(iuds)
    if iud_list:
        persons = Person.query.filter(Person.uid.in_(iud_list))
        return return_response([d.serialize() for d in persons if d])

    return return_response("Not Found", 404)