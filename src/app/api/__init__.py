"""
app/api/__init__.py


written by: Oliver Cordes 2019-02-01
changed by: Oliver Cordes 2019-02-01

"""

from flask import Blueprint

bp = Blueprint('api', __name__)


from app.api import access
