from flask import Flask
from flask_bootstrap import Bootstrap

from config import Config

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# define the app in the module ;-)
app = Flask(__name__)
app.config.from_object(Config)

# start the bootstrap code
bootstrap = Bootstrap(app)

# all database inits
db = SQLAlchemy(app)
migrate = Migrate(app, db)



# import the sub modules
from app import routes, models
