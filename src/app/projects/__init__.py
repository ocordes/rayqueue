"""
app/projects/__init__.py


written by: Oliver Cordes 2019-02-04
changed by: Oliver Cordes 2019-02-04

"""

from flask import Blueprint

bp = Blueprint('projects', __name__)


from app.projects import routes
