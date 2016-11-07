from .base import *

class GeoAddressDetails(db.Model, BaseModel):
    __tablename__ = 'address_details'
    __table_args__ = (
        UniqueConstraint('zip_code'),
        Index('address_details_zip_code_index', 'zip_code'),
        Index('address_details_lat_lon_index', 'latitude', 'longitude'),
    )
    id = db.Column(db.Integer, primary_key=True)
    zip_code = db.Column(db.Integer, index=True)
    county_name = db.Column(db.String(40), index=True)
    county_num = db.Column(db.String(5), index=True)
    county_type = db.Column(db.String(15))
    county_fips = db.Column(db.String(3))
    city = db.Column(db.String(128))
    state = db.Column(db.String(2))
    state_fips = db.Column(db.String(2))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)


class Address(db.Model, BaseModel):
    __table_args__ = (
        db.Index('npi_address_npi', 'npi', postgresql_using='hash'),
        db.Index('npi_address_zip_code', 'zip_code', postgresql_using='hash'),
        db.Index('npi_address_latitude', 'latitude', postgresql_using='hash'),
        db.Index('npi_address_longitude', 'longitude', postgresql_using='hash'),
        db.Index('npi_address_checksum', 'checksum', postgresql_using='hash'),
    )
    __tablename__ = 'address'
    __public__ = ['checksum', 'npi', 'zip_long', 'zip_code', 'state', 'city', 'street_address', 'street_address2',
                  'suppress_street_address2', 'phone_number', 'fax_number', 'primary', 'latitude', 'longitude',
                  'practice', 'handicap_access', 'hours', 'formatted_address', 'url_path', 'display_phone', 'address_type']
    checksum = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    npi = db.Column(db.BigInteger)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    zip_long = db.Column(db.String(32))
    zip_code = db.Column(db.Integer)
    state = db.Column(db.String(2))
    city = db.Column(db.String(50))
    street_address = db.Column(db.String(256))
    street_address2 = db.Column(db.String(256))
    suppress_street_address2 = db.Column(db.Boolean, default=False)
    formatted_address = db.Column(db.String(256))
    phone_number = db.Column(db.String(32))
    mobile_phone_number = db.Column(db.String(32))
    fax_number = db.Column(db.String(32))
    practice = db.Column(db.Boolean)
    primary = db.Column(db.Boolean, default=False)
    handicap_access = db.Column(db.Boolean, default=None)
    hours = db.Column(db.Text)
    url_path = db.Column(db.String(308))

    @property
    def address_type(self):
        if self.practice is None:
            return 'practice'
        return self.practice and 'practice' or 'mailing'

    @property
    def display_phone(self):
        if not self.phone_number:
            return

        if len(self.phone_number) <= 10:
            return "({}) {}-{}".format(self.phone_number[:3], self.phone_number[3:6], self.phone_number[6:])

        return self.phone_number

    @property
    def display_mobile_phone_number(self):
        if not self.mobile_phone_number:
            return

        if len(self.mobile_phone_number) <= 10:
            return "({}) {}-{}".format(self.mobile_phone_number[:3], self.mobile_phone_number[3:6], self.mobile_phone_number[6:])

        return self.mobile_phone_number
