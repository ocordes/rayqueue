"""

app/api/images.py

written by: Oliver Cordes 2019-03-07
changed by: Oliver Cordes 2019-03-11

"""


from datetime import datetime

from flask import current_app, make_response, abort, jsonify

from flask_login import current_user, login_user, logout_user, login_required

from app import db
from app.api import bp

from app.models import *

from app.api.checks import body_get

from app.queueing import queue_manager

import connexion



def get_image(user, token_info, image_id):
    image = Image.query.get(image_id)

    if image is None:
        abort(404, 'No image with such id')

    if image.user_id != user:
        abort(401, 'You are not the owner of this image')

    return jsonify(image.to_dict())



"""
image_clear_all

:param user:          the user info
:param token_info:    the token info
:param proejct_id:    the project_id to clear images
"""

def image_clear_all(user, token_info, project_id):
    project = Project.query.get(project_id)

    if project is None:
        abort(404, 'No project with such id')

    if project.user_id != user:
        abort(401, 'You are not the owner of this project')

    for image in project.images:
        ret, retmsg = image.remove()
        if ret:
            # image files were removed successfully
            # remove from database
            msg = 'Remove id=\'{}\' from Image'.format(image.id)
            db.session.delete(image)
        else:
            msg = 'Removing id=\'{}\' failed ({})'.format(image.id, retmsg)
        current_app.logger.info(msg)
    db.session.commit()

    return jsonify({'msg': 'OK'})



"""
image_upload_model

sends a file as a model and creates a new image instance

:param user:         the login user
:param token_info:   the request token
:param project_id:   the ID of the parent project
:param filename:     the FileStorage object

:rvalue:             json-object of the image data
"""

def image_upload_model(user, token_info, project_id, filename):
    project = Project.query.get(project_id)

    if project is None:
        abort(404, 'No project with such id')

    if project.user_id != user:
        abort(401, 'You are not the owner of this project')


    if (project.project_type == PROJECT_TYPE_IMAGE) and (project.status != PROJECT_OPEN):
        abort(401, 'Project is not open for new images')

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

    if (project.project_type == PROJECT_TYPE_ANIMATION) and (project.status != PROJECT_RENDERING):
        # update queue manager
        queue_manager.update()

    return jsonify(model_image.to_dict())



""""
image_upload_render_image

sends a file as the comlete rendered image to the image instance

:param user:         the login user
:param token_info:   the request token
:param image_id:     the ID of the parent image
:param filename:     the FileStorage object

:rvalue:             json-object of the image data
"""

def image_upload_render_image(user, token_info, image_id, filename):
    image = Image.query.get(image_id)

    if image is None:
        abort(404, 'No image with such id')

    if image.user_id != user:
        abort(401, 'You are not the owner of this image')


    # save the uploaded file and return the ID
    new_file = File.save_file(filename, filename.filename, FILE_RENDERED_IMAGE, project)
    db.session.add(new_file)
    db.session.commit()

    image.render_image = new_file.id

    db.session.commit()

    # update queue manager
    queue_manager.update()

    return jsonify(image.to_dict())



""""
image_upload_log_file

sends a file as the logfile to the rendered image to the image instance

:param user:         the login user
:param token_info:   the request token
:param image_id:     the ID of the parent image
:param filename:     the FileStorage object

:rvalue:             json-object of the image data
"""

def image_upload_log_file(user, token_info, image_id, filename):
    image = Image.query.get(image_id)

    if image is None:
        abort(404, 'No image with such id')

    if image.user_id != user:
        abort(401, 'You are not the owner of this image')


    # save the uploaded file and return the ID
    new_file = File.save_file(filename, filename.filename, FILE_RENDERED_IMAGE, project)
    db.session.add(new_file)
    db.session.commit()

    image.log_file = new_file.id

    db.session.commit()

    # update queue manager
    queue_manager.update()

    return jsonify(image.to_dict())



def queue_next(user, token_info):

    qe = queue_manager.next(user)

    if qe == None:
        return jsonify( {'msg': 'No images available'} )

    # wait for testing!
    ## prepare all files for rendering
    #qe.state = QueueElement.QUEUE_ELEMENT_RENDERING
    #qe.requested = datetime.utcnow()
    #qe.worker_id = user

    image = qe.image
    #image.state = Image.IMAGE_STATE_RENDERING

    ##db.session.commit()  # wait for testing!

    # return the image data
    return jsonify(image.to_dict())
