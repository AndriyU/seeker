import random
import _mysql
from functools import wraps
from sqlalchemy.sql.selectable import Select
from flask import request
from flask_sqlalchemy import SQLAlchemy as sqlA, SignallingSession, get_state
from urlparse import urlparse
import psycopg2
from flask import current_app


def db_raw_connect(db_connect_url):

    params = urlparse(db_connect_url)
    connection_params = {}
    if params.username:
        connection_params['user'] = params.username
    if params.password:
        connection_params['password'] = params.password
    if params.port:
        connection_params['port'] = params.port
    if params.hostname:
        connection_params['host'] = params.hostname
    connection_params['database'] = params.path.strip('/')
    connection_params['client_encoding'] = 'UTF8'
    return psycopg2.connect(**connection_params)


def use_slave(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        request._use_slave = True
        return fn(*args, **kwargs)

    return wrapper


class RoutingSession(SignallingSession):
    def get_bind(self, mapper, clause=None):
        parent_bind = super(RoutingSession, self).get_bind(mapper, clause)
        if not hasattr(request, '_use_slave'):
            return parent_bind

        if not isinstance(clause, Select):
            return parent_bind

        if not current_app.config.get('SQLALCHEMY_SLAVE_BIND_NAMES'):
            return parent_bind

        state = get_state(self.app)
        return state.db.get_engine(self.app, bind=random.choice(current_app.config['SQLALCHEMY_SLAVE_BIND_NAMES']))


class SQLAlchemy(sqlA):
    def create_session(self, options):
        return RoutingSession(self, **options)


class SphinxMysql():
    config = {
        'SPHINX_HOST': '127.0.0.1',
        'SPHINX_PORT': 3307
    }

    def init_app(self, config=None):
        "This is used to initialize cache with your app object"
        if not (config is None or isinstance(config, dict)):
            raise ValueError("`config` must be an instance of dict or None")
        self.config = config

    def connection(self):
        return _mysql.connect(host=self.config['SPHINX_HOST'], port=int(self.config['SPHINX_PORT']))

    def cursor(self):
        return self.connection.cursor()