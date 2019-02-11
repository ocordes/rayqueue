"""

api/projects.py

written by: Oliver Cordes 2019-02-11
changed by: Oliver Cordes 2019-02-11

"""


from datetime import datetime

from flask import current_app, make_response, abort, jsonify

from flask_login import current_user, login_user, logout_user, login_required

#from app import db
from app.api import bp

from app.models import User, Project

from time import time
import jwt
import six



def find_projects(user, token_info):
    u = User.query.get(int(user))

    data = [p.to_dict() for p in u.projects.all()]

    return jsonify(data)
