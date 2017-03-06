from root import fields
from webargs.flaskparser import use_kwargs
from sqlalchemy import func, or_, and_, desc

from extra import db
from ..views import api
from ..utils import return_response, split_re
from extra.models.service import ServiceDetails, MyService


@api.route('/service/<any(batch):batch>/<any(short):short>/')
@api.route('/service/<any(batch):batch>/', defaults={'short': None})
@api.route('/service/', defaults={'batch': None, 'short': None})
@use_kwargs({
    'codes': fields.request_string,
    'code': fields.request_string
})
def service(batch, short, codes, code):
    if batch:
        query = db.session.query(ServiceDetails).order_by(ServiceDetails.display_name)
        if codes:
            query = query.filter(ServiceDetails.code.in_(split_re.split(codes)))
        if short:
            query = query.values(ServiceDetails.code, ServiceDetails.display_name, ServiceDetails.url_path,
                                 ServiceDetails.description, ServiceDetails.synonyms, ServiceDetails.definition,
                                 ServiceDetails.notes)
            return return_response([s for s in query])
        else:
            return return_response([s.serialize() for s in query.all()])
    else:
        if not code or short:
            return return_response('Precondition Failed', 412)
        service = ServiceDetails.query.get_or_404(code)
        return return_response(service.serialize())


@api.route('/service/autocomplete/')
# @cache.memoize()
@use_kwargs({
    'query': fields.request_string,
    'limit': fields.limit,
    'order_by': fields.request_string,
    'order_type': fields.sord
})
def autocomplete_by_service(query, limit, order_by, order_type):
    search_query = db.session.query(
                                    SpecialtyInfo.classification,
                                    SpecialtyInfo.specialization,
                                    SpecialtyInfo.display_name,
                                    SpecialtyInfo.code,
                                    SpecialtyInfo.description,
                                    SpecialtyInfo.popularity,
                                    SpecialtyInfo.url_path)
    if query:
        search_query = search_query.filter(
            or_(SpecialtyInfo.classification.ilike("%{}%".format(query)),
                SpecialtyInfo.display_name.ilike("%{}%".format(query)),
                SpecialtyInfo.specialization.ilike("%{}%".format(query)),
                SpecialtyInfo.synonyms.ilike("%{}%".format(query)),
                ))
    if order_by and order_by in ['popularity', 'display_name']:
        if order_type == 'desc':
            search_query = search_query.order_by(desc(order_by))
        else:
            search_query = search_query.order_by(order_by)
    else:
        search_query = search_query.order_by(SpecialtyInfo.display_name)
    specialties = search_query.limit(limit)

    return return_response([s._asdict() for s in specialties])