"""

app/__init__.py

written by: Oliver Cordes 2019-01-26
changed by: Oliver Cordes 2019-01-30

"""

import os
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler

from config import Config

import connexion

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail



db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'
mail = Mail()
bootstrap = Bootstrap()
#moment = Moment()
#babel = Babel()

# define the app in the module ;-)


def create_app(config_class=Config):

    app = connexion.App(__name__, specification_dir='./api/')
    # Read the swagger.yml file to configure the endpoints
    app.add_api('openapi.yaml')

    # attach the config
    app.app.config.from_object(Config)

    db.init_app(app.app)
    migrate.init_app(app.app, db)
    login.init_app(app.app)
    mail.init_app(app.app)
    bootstrap.init_app(app.app)
    #moment.init_app(app.app)
    #babel.init_app(app.app)


    # register the blueprints
    from app.errors import bp as errors_bp
    app.app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    #app.register_blueprint(auth_bp, url_prefix='/auth')
    app.app.register_blueprint(auth_bp)

    from app.api import bp as api_bp
    app.app.register_blueprint(api_bp)


    from app.main import bp as main_bp
    app.app.register_blueprint(main_bp)

    # data dir
    if not os.path.exists(app.app.config['DATA_DIR']):
        os.mkdir(app.app.config['DATA_DIR'])

    # error handler
    if not app.app.debug:
        if app.app.config['MAIL_SERVER']:
            auth = None
            if app.app.config['MAIL_USERNAME'] or app.app.config['MAIL_PASSWORD']:
                auth = (app.app.config['MAIL_USERNAME'], app.app.config['MAIL_PASSWORD'])
            secure = None
            if app.app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.app.config['MAIL_SERVER'], app.app.config['MAIL_PORT']),
                #fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                fromaddr='ocordes@astro.uni-bonn.de',
                toaddrs=app.app.config['ADMINS'], subject='Rayqueue Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.app.logger.addHandler(mail_handler)


            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/rayqueue.log', maxBytes=10240,
                                       backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.app.logger.addHandler(file_handler)

            app.app.logger.setLevel(logging.INFO)
            app.app.logger.info('Rayqueue startup')

        return app


# import the sub modules
from app import models
