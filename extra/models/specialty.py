from .base_model import *


class SpecialtyReasonToVisit(db.Model, Serializer):
    __tablename__ = 'specialty_reason_to_visit'

    reason_id = db.Column(db.Integer, primary_key=True)
    specialty_id = db.Column(db.Integer, db.ForeignKey('public.specialty.id'), nullable=False)
    reason_text = db.Column(db.Text, default='')


class SpecialtyInfo(db.Model, BaseModel):
    __tablename__ = 'specialty'
    __table_args__ = {'schema': 'public'}

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True)
    type = db.Column(db.String(256))
    classification = db.Column(db.String(512))
    specialization = db.Column(db.String(512))
    definition = db.Column(db.Text)
    notes = db.Column(db.Text)
    display_name = db.Column(db.String(512), default='')
    description = db.Column(db.Text, default='', nullable=False)
    url_path = db.Column(db.String(512))
    synonyms = db.Column(db.Text)
    popularity = db.Column(db.Integer)

    reason_to_visit = db.relationship('SpecialtyReasonToVisit',
                                      primaryjoin=id == SpecialtyReasonToVisit.specialty_id,
                                      backref='specialties')


class MySpecialty(db.Model, BaseModel):
    __tablename__ = 'person_specialty'
    __table_args__ = (db.Index('person_specialty_person_uid_idx', 'person_uid', postgresql_using='hash'),
                      db.Index('person_specialty_specialty_code_idx', 'specialty_code', postgresql_using='hash'))
    __public__ = ['specialty_code', 'license_number', 'license_start', 'license_end', 'primary', 'board_name',
                  'board_eligible', 'board_certified', 'board_permanent', 'classification', 'specialization']

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    person_uid = db.Column(db.BigInteger)
    specialty_code = db.Column(db.String(10))
    license_number = db.Column(db.String(20))
    license_start = db.Column(db.Date)
    license_end = db.Column(db.Date)
    primary = db.Column(db.Boolean)
    board_name = db.Column(db.String(128))
    board_eligible = db.Column(db.Boolean)
    board_certified = db.Column(db.String(1))
    board_permanent = db.Column(db.Boolean)
    update_id = db.Column(db.Integer)
    state = db.Column(db.String(2))

    @property
    def classification(self):
        classification = db.session.query(SpecialtyInfo.classification).\
            filter(SpecialtyInfo.code == self.specialty_code).first()
        return classification and classification[0]

    @property
    def specialization(self):
        specialization = db.session.query(SpecialtyInfo.specialization).\
            filter(SpecialtyInfo.code == self.specialty_code).first()
        return specialization and specialization[0]
