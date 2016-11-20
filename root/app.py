# -*- coding: utf-8 -*-
#pylint:disable-msg=W0612

import sys
import os
from pprint import pprint
from flask import Flask, jsonify
from extra import db

reload(sys)
sys.setdefaultencoding('utf-8')


# blueprints
from root.api.views import api

__all__ = ['create_app']

BLUEPRINTS = (
    api,
)


def create_app(config=None, app_name='core_api', blueprints=None):
    app = Flask(
        app_name
    )

    app.config.from_object('root.config')
    app.config.from_pyfile('local.cfg', silent=True)

    if config:
        app.config.from_pyfile(config)

    if blueprints is None:
        blueprints = BLUEPRINTS
    blueprints_fabrics(app, blueprints)
    extensions_fabrics(app)
    error_pages(app)
    configure_logging(app)

    return app


def blueprints_fabrics(app, blueprints):
    """Configure blueprints in views."""

    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def extensions_fabrics(app):
    db.init_app(app)


def error_pages(app):
    @app.errorhandler(422)
    def web_args(error):
        messages = error.data.get('messages', [])
        return jsonify({'errors': messages}), 412

    @app.errorhandler(404)
    def page_not_found(error):
        return jsonify({'errors': 'Not found'}), 404


def configure_logging(app):
    """Configure file(info) and email(error) logging."""

    #if app.debug or app.testing:
        # Skip debug and test mode. Just check standard output.
        #return

    import logging.handlers
    import logging

    app.logger.setLevel(app.config['LOG_LEVEL'])
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s [in view %(pathname)s:%(lineno)d]:\n%(message)s',
                                  '%d/%m/%Y %H:%M:%S')

    info_log = os.path.join(app.config['LOG_FOLDER'], 'info.log')
    info_file_handler = logging.handlers.RotatingFileHandler(info_log, maxBytes=100000, backupCount=10)
    info_file_handler.setLevel(logging.INFO)
    info_file_handler.setFormatter(formatter)

    error_log = os.path.join(app.config['LOG_FOLDER'], 'error.log')
    error_log = logging.handlers.RotatingFileHandler(error_log, maxBytes=100000, backupCount=10)
    error_log.setLevel(logging.ERROR)
    error_log.setFormatter(formatter)

    app.logger.addHandler(info_file_handler)
    app.logger.addHandler(error_log)

    # USAGE
    # from flask import current_app as ca
    # ca.logger.debug(pformat({'key': 'val'}))
    # ca.logger.info(pformat({'key': 'val'}))
    # ca.logger.warn('logger warn')
    # ca.logger.error('logger error')
    # ca.logger.fatal('logger fatal')