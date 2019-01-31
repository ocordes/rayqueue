"""
app/errors/__init__.py


written by: Oliver Cordes 2019-01-31
changed by: Oliver Cordes 2019-01-31

"""

from flask import Blueprint

bp = Blueprint('errors', __name__)

from app.errors import handlers
