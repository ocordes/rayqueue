import os
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler

from config import Config

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail


# define the app in the module ;-)
app = Flask(__name__)
app.config.from_object(Config)

# start the bootstrap code
bootstrap = Bootstrap(app)

# all database inits
db = SQLAlchemy(app)
migrate = Migrate(app, db)

mail = Mail(app)


# login manager
login = LoginManager(app)
login.login_view = 'login'


# data dir
if not os.path.exists(app.config['DATA_DIR']):
    os.mkdir(app.config['DATA_DIR'])

# error handler
if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            #fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            fromaddr='ocordes@astro.uni-bonn.de',
            toaddrs=app.config['ADMINS'], subject='Rayqueue Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/rayqueue.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Rayqueue startup')


# import the sub modules
from app import routes, models, errors
