from .base_model import *
from sqlalchemy import PrimaryKeyConstraint

from .address import Address
from specialty import SpecialtyDetails, MySpecialty, SpecialtyReasonToVisit
from service import MyService


class Organization(db.Model, BaseModel):
    __tablename__ = 'organization'
    __table_args__ = (
        db.Index('organization_id_key', 'id', postgresql_using='hash'),
        db.Index('organization_npi_key', 'npi', postgresql_using='hash'),
        db.Index('organization_cuid_key', 'cuid', postgresql_using='hash'),
        db.Index('organization_other_name', 'other_name', postgresql_using='gin',
                 postgresql_ops={'other_name': 'gin_trgm_ops'}),
        db.Index('organization_name', 'name', postgresql_using='gin',
                 postgresql_ops={'name': 'gin_trgm_ops'}),
    )
    __public__ = ['id', 'npi', 'cuid'
                  'phone_number', 'name', 'other_name', 'types', 'active', 'active_change_date',
                  'url_path', 'addresses', 'display_phone']

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    id_type = db.Column(db.Enum('npi', 'cuid', 'uid', 'barcode', name='organization_id_type_ext'))
    name = db.Column(db.String(255))
    other_name = db.Column(db.String(255))
    short_name = db.Column(db.String(100))
    types = db.Column(ARRAY(VARCHAR(255)))
    active = db.Column(db.Boolean)
    active_change_date = db.Column(db.Date, default=None)
    url_path = db.Column(db.String(512))
    update_id = db.Column(db.Integer)

    @property
    def addresses(self):
        return [a.serialize() for a in Address.query.filter(
            Address.npi == self.npi
        ).all()]

    @property
    def addresses(self):
        return Address.query.filter(
            Address.npi == self.npi,
            or_(Address.practice == True, Address.practice.is_(None))
        ).all()

    @property
    def specialty_codes(self):
        return db.session.query(MySpecialty.specialty_code).filter(MySpecialty.person_id == self.id).all()

    @property
    def specialties(self):
        return SpecialtyDetails.query.filter(MySpecialty.person_id == self.id).all()

    @property
    def reasons_to_visit(self):
        specialties_codes = [s[0] for s in self.specialty_codes]
        return SpecialtyReasonToVisit.query. \
            join(SpecialtyDetails, SpecialtyReasonToVisit.specialty_id == SpecialtyDetails.id). \
            filter(SpecialtyDetails.code.in_(specialties_codes)).all()

    @property
    def services(self):
        return MyService.query.filter(MyService.person_id == self.id).all()