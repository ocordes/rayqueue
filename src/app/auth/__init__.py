"""

app/auth/__init__.py

written by: Oliver Cordes 2019-02-01
changed by: Oliver Cordes 2019-02-02

"""


from flask import Blueprint

bp = Blueprint('auth', __name__)

from app.auth import routes, users
