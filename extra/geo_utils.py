from sqlalchemy import func
from extra import db
from math import sin, cos, radians, degrees, acos
import re
from extra.models.address import GeoAddressDetails
KILOMETERS_TO_MILES_FACTOR = 1.60934
SEARCH_ALLOWED_CHARACTERS = re.compile('[^0-9a-zA-Z _\-\.,]')


def calculate_distance(lat1, long1, lat2, long2):
    try:
        distance = (sin(radians(lat1)) * sin(radians(lat2)) +
                    cos(radians(lat1)) * cos(radians(lat2)) * cos(radians(long1 - long2)))
    except TypeError:
        return float('inf')

    try:
        distance = degrees(acos(distance)) * 69.09
    except ValueError:
        distance = 0.0
    return distance


def get_coordinates(latitude, longitude, zip_code, city, state):
    if latitude and longitude:
        return latitude, longitude

    if zip_code:
        point = GeoAddressDetails.query.get(zip_code)
        if not point:
            return 0, 0
        return point.latitude, point.longitude
    elif city and state:
        latitude, longitude = db.session.query(func.avg(GeoAddressDetails.latitude).label('latitude'),
                                               func.avg(GeoAddressDetails.longitude).label('longitude')).\
            filter(GeoAddressDetails.city == city.title(), GeoAddressDetails.state == state.upper()).all()[0]
        return latitude or 0, longitude or 0
    return 0, 0


def get_address_details(address):
    points = db.session.query(GeoAddressDetails.state, GeoAddressDetails.city, GeoAddressDetails.zip_code, GeoAddressDetails.latitude,
                              GeoAddressDetails.longitude, GeoAddressDetails.county_name, GeoAddressDetails.county_num)
    if address.get('state'):
        points = points.filter(GeoAddressDetails.state.ilike(address['state']))
    if address.get('city'):
        points = points.filter(GeoAddressDetails.city.ilike(re.sub('[-\s]', '_', address['city'])))
    if address.get('county'):
        points = points.filter(GeoAddressDetails.county_name.ilike(re.sub('[-\s]', '_', address['county'])))
    if address.get('zip_code'):
        points = points.filter(GeoAddressDetails.zip_code == address['zip_code'])
    points = points.order_by(GeoAddressDetails.state, GeoAddressDetails.city, GeoAddressDetails.zip_code)
    # print points.statement.compile(compile_kwargs={"literal_binds": True})
    return [
        {'state': point.state, 'city': point.city, 'county': point.county_name, 'county_num': point.county_num,
         'zip_code': point.zip_code, 'latitude': point.latitude, 'longitude': point.longitude}
        for point in points.all()]