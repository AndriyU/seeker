from root import fields
from webargs.flaskparser import use_kwargs
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
def doctor_specialty_group(batch, short, codes, code):
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
        specialty_group = SpecialtyDetails.query.get_or_404(code)
        return return_response(specialty_group.serialize())
