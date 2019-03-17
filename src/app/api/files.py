"""

api/files.py

written by: Oliver Cordes 2019-03-07
changed by: Oliver Cordes 2019-03-07

"""


from datetime import datetime

from flask import current_app, make_response, abort, jsonify, send_file

from flask_login import current_user, login_user, logout_user, login_required

from app import db
from app.api import bp

from app.models import User, Project, File

from app.api.checks import body_get


"""
get_file_by_id
"""

def get_file_by_id(user, token_info, file_id):
    ffile = File.query.get(file_id)

    if ffile is None:
        abort(404, 'No file with such id')

    if ffile.user_id != user:
        abort(401, 'You are not the owner of this file')


    filename = ffile.full_filename()
    orig_name = ffile.name[37:]
    return send_file(filename, as_attachment=True, attachment_filename=orig_name)



"""
get_file_db_by_id
"""

def get_file_db_by_id(user, token_info, file_id):
    ffile = File.query.get(file_id)

    if ffile is None:
        abort(404, 'No file with such id')

    if ffile.user_id != user:
        abort(401, 'You are not the owner of this file')


    return jsonify(ffile.to_dict())
