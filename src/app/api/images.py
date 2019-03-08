"""

api/images.py

written by: Oliver Cordes 2019-03-07
changed by: Oliver Cordes 2019-03-07

"""


from datetime import datetime

from flask import current_app, make_response, abort, jsonify

from flask_login import current_user, login_user, logout_user, login_required

from app import db
from app.api import bp

from app.models import User, Project, File, Image, \
                    FILE_MODEL

from app.api.checks import body_get

import connexion


def image_upload_model(user, token_info, project_id, filename):
    project = Project.query.get(project_id)

    if project is None:
        abort(404, 'No project with such id')

    if project.user_id != user:
        abort(401, 'You are not the owner of this project')

    # save the uploaded file and return the ID
    new_file = File.save_file(filename, filename.filename, FILE_MODEL, project)
    db.session.add(new_file)
    db.session.commit()
    print(new_file.id)

    model_image = Image(user_id=user,
                        project_id=project_id,
                        model=new_file.id)

    db.session.add(model_image)
    db.session.commit()

    return jsonify(model_image.to_dict())
    
