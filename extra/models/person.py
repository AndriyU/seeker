from .base_model import *
from address import Address
from specialty import SpecialtyDetails, MySpecialty, SpecialtyReasonToVisit
from service import MyService


class Person(db.Model, BaseModel):
    __tablename__ = 'person'
    __table_args__ = (
        
        db.Index('person_first_name_index', 'first_name', postgresql_using='gin',
                 postgresql_ops={'first_name': 'gin_trgm_ops'}),
        db.Index('person_first_name_pcp_index', 'first_name', postgresql_using='gin',
                  postgresql_ops={'first_name': 'gin_trgm_ops'}, postgresql_where=text('pcp = True')),
        db.Index('person_last_name_index', 'last_name', postgresql_using='gin',
                 postgresql_ops={'last_name': 'gin_trgm_ops'}),
        db.Index('person_last_name_pcp_index', 'last_name', postgresql_using='gin',
                 postgresql_ops={'last_name': 'gin_trgm_ops'}, postgresql_where=text('pcp is True')),
    )

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    npi = db.Column(db.BigInteger, autoincrement=False)
    first_name = db.Column(db.String(50))
    middle_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    suffix = db.Column(db.String(10))
    gender = db.Column(db.String(1))
    credential = db.Column(db.String(20))
    rating = db.Column(db.Float)
    update_id = db.Column(db.Integer)

    def __unicode__(self):
        return self.person_title

    @property
    def person_title(self):
        return u"{name}{middle} {last}{suffix}{credential}".format(
            name=self.first_name,
            middle=self.middle_name and u' {}'.format(self.middle_name) or '',
            last=self.last_name,
            suffix=self.suffix and u' {}'.format(self.suffix) or '',
            credential= self.credential and u', {}'.format(self.credential.replace('.', '')) or ''
        )

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