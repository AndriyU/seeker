from root import fields
from webargs.flaskparser import use_kwargs
from sqlalchemy import func, or_, and_, desc

from extra import db
from ..views import api
from ..utils import return_response, split_re
from extra.models.specialty import SpecialtyDetails, MySpecialty


@api.route('/specialty/<any(batch):batch>/<any(short):short>/')
@api.route('/specialty/<any(batch):batch>/', defaults={'short': None})
@api.route('/specialty/', defaults={'batch': None, 'short': None})
@use_kwargs({
    'codes': fields.request_string,
    'code': fields.request_string
})
def specialty(batch, short, codes, code):
    if batch:
        query = db.session.query(SpecialtyDetails).order_by(SpecialtyDetails.display_name)
        if codes:
            query = query.filter(SpecialtyDetails.code.in_(split_re.split(codes)))
        if short:
            query = query.values(SpecialtyDetails.code, SpecialtyDetails.display_name, SpecialtyDetails.url_path,
                                 SpecialtyDetails.description, SpecialtyDetails.classification, SpecialtyDetails.specialization,
                                 SpecialtyDetails.synonyms)
            return return_response([s for s in query])
        else:
            return return_response([s.serialize() for s in query.all()])
    else:
        if not code or short:
            return return_response('Precondition Failed', 412)
        sp= SpecialtyDetails.query.get_or_404(code)
        return return_response(sp.serialize())


def get_specialty_code(url_path):
    s = db.session.query(SpecialtyDetails.code).filter(SpecialtyDetails.url_path==url_path).first()
    if s:
        return s[0]


def get_specialty_url_path(code):
    s = db.session.query(SpecialtyDetails.url_path).filter(SpecialtyDetails.code==code).first()
    if s:
        return s[0]


@api.route('/specialty/autocomplete/')
# @cache.memoize()
@use_kwargs({
    'query': fields.request_string,
    'limit': fields.limit,
    'order_by': fields.request_string,
    'order_type': fields.sord
})
def autocomplete_by_specialty(query, limit, order_by, order_type):
    search_query = db.session.query(
                                    SpecialtyDetails.classification,
                                    SpecialtyDetails.specialization,
                                    SpecialtyDetails.display_name,
                                    SpecialtyDetails.code,
                                    SpecialtyDetails.description,
                                    SpecialtyDetails.popularity,
                                    SpecialtyDetails.url_path)
    if query:
        search_query = search_query.filter(
            or_(SpecialtyDetails.classification.ilike("%{}%".format(query)),
                SpecialtyDetails.display_name.ilike("%{}%".format(query)),
                SpecialtyDetails.specialization.ilike("%{}%".format(query)),
                SpecialtyDetails.synonyms.ilike("%{}%".format(query)),
                ))
    if order_by and order_by in ['popularity', 'display_name']:
        if order_type == 'desc':
            search_query = search_query.order_by(desc(order_by))
        else:
            search_query = search_query.order_by(order_by)
    else:
        search_query = search_query.order_by(SpecialtyDetails.display_name)
    specialties = search_query.limit(limit)

    return return_response([s._asdict() for s in specialties])