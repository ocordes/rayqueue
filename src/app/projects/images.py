"""

app/projects/images.py

written by: Oliver Cordes 2019-03-12
changed by: Oliver Cordes 2020-02-29

"""

import os
from datetime import datetime

from flask import current_app, request, render_template, \
                  url_for, flash, redirect, send_file
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename


from app import db
from app.projects import bp
from app.projects.forms import CreateProjectForm, UpdateProjectForm, \
                               ProjectListForm,\
                               ManageBaseFileForm, ManageImageForm
from app.projects.admin import owner_required, check_access
from app.models import *

from app.utils.files import size2human, read_logfile
from app.utils.backref import get_redirect_target


@bp.route('/image/<imageid>', methods=['GET'])
@login_required
def show_image(imageid):
    target = get_redirect_target()

    image = Image.query.get(imageid)

    if image is None:
        return redirect(url_for('main.index'))

    if (image.user_id != current_user.id) and (current_user.administrator == False):
        flash('You are not allowed to view this image!')
        return redirect(target)

    logfile_data = ''

    if image.log_file != -1:
        # get logfile for webpage
        logfile = File.query.get(image.log_file)
        logfile_data = read_logfile(logfile.full_filename())


    return render_template('projects/show_image.html',
                            title='Image',
                            logfile_data=logfile_data,
                            image=image )


"""
get_render_image

gives rendered image to the browser for displaying.
This link is not meant to be used as a download option, use
get_project_file instead!
"""
@bp.route('/image/<imageid>/render_image', methods=['GET'])
@login_required
def get_render_image(imageid):
    target = get_redirect_target()

    image = Image.query.get(imageid)

    if image is None:
        return redirect(url_for('main.index'))

    if (image.user_id != current_user.id) and (current_user.administrator == False):
        flash('You are not allowed to view this image!')
        return redirect(target)

    ffile = File.query.get(image.render_image)

    filename = ffile.full_filename()

    return send_file(filename)


"""
get_render_icon

gives the icon of the rendered image to the browser for displaying.
This link is not meant to be used as a download option, use
get_project_file instead!
"""
@bp.route('/image/<imageid>/render_icon', methods=['GET'])
@login_required
def get_render_icon(imageid):
    target = get_redirect_target()

    image = Image.query.get(imageid)

    if image is None:
        return redirect(url_for('main.index'))

    if (image.user_id != current_user.id) and (current_user.administrator == False):
        flash('You are not allowed to view this image!')
        return redirect(target)

    ffile = File.query.get(image.render_image)

    filename = ffile.full_icon_name()

    return send_file(filename)
