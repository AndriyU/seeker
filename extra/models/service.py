from .base_model import *


class ServiceDetails(db.Model, BaseModel):
    __tablename__ = 'service'

    code = db.Column(db.String(5), primary_key=True, autoincrement=False)
    description = db.Column(db.String(256))
    type = db.Column(db.String(256))
    definition = db.Column(db.Text)
    notes = db.Column(db.Text)
    display_name = db.Column(db.String(512), default='')
    url_path = db.Column(db.String(512))
    synonyms = db.Column(db.Text)
    popularity = db.Column(db.Integer)
    

class MyService(db.Model, BaseModel):
    __tablename__ = 'person_service'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    person_uid = db.Column(db.BigInteger, index=True)
    code = db.Column(db.String(5))
    place_of_service = db.Column(db.String(50))
    number_of_services = db.Column(db.Integer)
    average_price = db.Column(db.Float)
    year = db.Column(db.Integer)
    url_path = db.Column(db.String(512))

    @property
    def service_details(self):
        return ServiceDetails.query.filter(ServiceDetails.code == self.code).first()
