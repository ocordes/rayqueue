from flask import Flask
from flask_bootstrap import Bootstrap

from config import Config

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_login import LoginManager

# define the app in the module ;-)
app = Flask(__name__)
app.config.from_object(Config)

# start the bootstrap code
bootstrap = Bootstrap(app)

# all database inits
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# login manager
login = LoginManager(app)
login.login_view = 'login'



# import the sub modules
from app import routes, models
