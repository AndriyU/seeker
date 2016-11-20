# -*- coding: utf-8 -*-
DEBUG = False
SECRET_KEY = '\xb6\x14\x9c\xf8\xcc\xeb\x8e\x86\x11\xbc\x8b\x94\x08\x10\x1c\xe4wU\x9dOg<f?'  # for csfr form
AUTHORIZATION_KEY = 'f783SW4SdejcnS1OI893475DE2dg547u'

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://user:Passw0rd!@127.0.0.1:5432/core?connect_timeout=30'
SQLALCHEMY_TRACK_MODIFICATIONS = True

LOG_LEVEL = 30
#CRITICAL = FATAL = 50
#ERROR = 40
#WARNING = WARN = 30
#INFO = 20
#DEBUG = 10
#NOTSET = 0

LOG_FOLDER = '../log/'
