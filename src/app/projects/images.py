"""

app/projects/images.py

written by: Oliver Cordes 2019-03-12
changed by: Oliver Cordes 2019-03-12

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
                               ProjectListForm, UploadBaseFilesForm, \
                               ManageBaseFileForm, ManageImageForm
from app.projects.admin import owner_required, check_access
from app.models import *

from app.utils.files import size2human
from app.utils.backref import get_redirect_target


@bp.route('/image/<imageid>', methods=['GET'])
@login_required
def show_image(imageid):
    target = get_redirect_target()

    image = Image.query.get(imageid)

    if (image.user_id != current_user.id) and (current_user.administrator == False):
        flash('You are not allowed to view this image!')
        return redirect(target)

    return render_template('projects/show_image.html',
                            title='Image',
                            image=image )
