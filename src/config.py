"""

config.py

written by: Oliver Cordes 2019-01-31
changed by: Oliver Cordes 2020-03-29

"""

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    DATA_DIR   = os.environ.get('DATA_DIR') or os.path.join(basedir, 'data')

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    #ADMINS = ['your-email@example.com']
    ADMINS = ['ocordes@astro.uni-bonn.de']

    # debug toolbar configs
    DEBUG = os.environ.get('APP_DEBUG') == 'True'
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # scheduler configs
    SCHEDULER_API_ENABLED = True


    # gunicorn check
    SERVER_SOFTWARE = os.environ.get('SERVER_SOFTWARE') or 'FLASK'

    # terminal Settings
    CMD = os.environ.get('TERMINAL_CMD') or '/bin/bash'

    # flickr API keys
    FLICKR_API_KEY = os.environ.get('FLICKR_API_KEY') or None
    FLICKR_API_SECRET = os.environ.get('FLICKR_API_SECRET') or None
