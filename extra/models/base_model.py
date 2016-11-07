from datetime import datetime
from sqlalchemy import and_, or_, not_, func, Index, UniqueConstraint, text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import foreign, remote
from sqlalchemy.dialects.postgresql import ARRAY, VARCHAR
from itertools import chain
from extra import db
from extra.utils import Serializer


class BaseModel(object, Serializer):

    @classmethod
    def full_name(self):
        return '.'.join((self.__table__.schema, self.__table__.name))
