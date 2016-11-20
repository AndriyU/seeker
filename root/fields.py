import re
from webargs import fields, validate, ValidationError
from us import STATES
from api.utils import split_re, is_digit
from extra import db, DEFAULT_LIMIT, MAX_LIMIT, CURRENT_YEAR

DISALLOWED_CHARACTERS = re.compile(r"[\"\'=\[\]]")


def validate_query_string(field):
    if DISALLOWED_CHARACTERS.search(field):
        raise ValidationError('Disallowed character detected')
    try:
        field.decode('ascii')
    except UnicodeDecodeError:
        raise ValidationError('Disallowed encoding of request string')

    if len(field) and len(field.strip()) == 0:
        raise ValidationError('Empty request string. Only Space character not allowed in string.')


def validate_integer_string_list(field):
    validate_query_string(field)
    for num in split_re.split(field):
        if num and not is_digit(num.strip()):
            raise ValidationError('Not a valid coma-separated list of integers')

    if len(split_re.split(field)) > MAX_LIMIT:
        raise ValidationError('Request Entity Too Large')


def validate_map_size(field):
    size = field.split('x')
    if len(size) != 2 or not size[0].isdigit() or not size[1].isdigit():
        raise ValidationError('Wrong size format. Required example: 100x100')


# GENERAL
request_string_required = fields.Str(required=True, validate=[validate_query_string, validate.Length(min=1)])
request_string = fields.Str(required=False, missing=None, validate=validate_query_string)
request_int_required = fields.Int(required=True, validate=validate.Range(min=1))
request_int = fields.Int(required=False, missing=None, validate=validate.Range(min=1))
request_int_list_required = fields.Str(required=True, validate=[validate_integer_string_list, validate.Length(min=1)])
request_int_list = fields.Str(required=False, missing=None, validate=validate_integer_string_list)

year = fields.Int(missing=CURRENT_YEAR, required=False, validate=validate.Range(min=1970))
true_false = fields.Str(required=False, missing=None, validate=validate.OneOf(['true', 'false']))
bool_field = fields.Bool(required=False, missing=None)
sord = fields.Str(required=False, missing='asc', validate=validate.OneOf(['asc', 'desc']))
limit = fields.Int(missing=DEFAULT_LIMIT, required=False, validate=validate.Range(min=1, max=MAX_LIMIT))
offset = fields.Int(missing=0, required=False, validate=validate.Range(min=0))
page = fields.Int(missing=1, required=False, validate=validate.Range(min=1))
gender_short = fields.Str(required=False, missing=None, validate=validate.OneOf(['m', 'f']))
gender = fields.Str(required=False, missing=None, validate=validate.OneOf(['male', 'female']))

# GEO
radius = fields.Int(missing=10, validate=validate.Range(min=1))
latitude = fields.Float(required=False, missing=None)
longitude = fields.Float(required=False, missing=None)
latitude_req = fields.Float(required=True)
longitude_req = fields.Float(required=True)
zip_code = fields.Int(required=False, missing=None, validate=validate.Range(min=1, max=100000))
zip_code_req = fields.Int(required=True, validate=validate.Range(min=1, max=100000))
state = fields.Str(required=False, missing=None, validate=validate.OneOf([s.abbr for s in STATES] + [s.abbr.lower() for s in STATES]))
city = fields.Str(required=False, missing=None, validate=validate_query_string)
county = fields.Str(required=False, missing=None, validate=validate_query_string)

# Static MAP
map_format = fields.Str(required=False, missing='PNG', validate=validate.OneOf(('GIF', 'JPEG', 'PNG')))
map_type = fields.Str(required=False, missing='roadmap', validate=validate.OneOf(('roadmap', 'satellite', 'hybrid', 'terrain')))
map_size = fields.Str(required=False, missing='298x97', validate=validate_map_size)
address_query = fields.Str(required=True)