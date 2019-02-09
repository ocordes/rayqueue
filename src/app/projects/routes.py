"""

app/projects/routes.py

written by: Oliver Cordes 2019-02-04
changed by: Oliver Cordes 2019-02-05

"""

import os
from datetime import datetime

from flask import current_app, request, render_template, \
                  url_for, flash, redirect
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse


from app import db
from app.projects import bp
from app.projects.forms import CreateProjectForm, UpdateProjectForm
from app.projects.admin import owner_required, check_access
from app.models import User, Project
#from app.auth.email import send_password_reset_email, send_email_verify_email




@bp.route('/project/<projectid>', methods=['GET','POST'])
@owner_required('projectid')
@login_required
def show_project(projectid):
    form = UpdateProjectForm()

    project = Project.query.get(projectid)

    if form.validate_on_submit():
        pass
    elif request.method == 'GET':
        form.name.data = project.name
        
    return render_template('projects/show_project.html',
                            title='Project',
                            form=form)


@bp.route('/projects', methods=['GET','POST'])
@login_required
def show_projects():
    projects = None
    pr = Project.query.all()
    for p in pr:
        ret, msg = check_access(current_user, p)
        if ret:
            if projects is None:
                projects = [p]
            else:
                projects.append(p)
    return render_template('projects/show_projects.html',
                            title='Project list',
                            projects=projects,
                            user_id=User.query.get)


@bp.route('/create_project', methods=['GET','POST'])
@login_required
def create_project():
    form = CreateProjectForm()

    if form.validate_on_submit():
        project = Project(name=form.name.data,
                          is_public=form.is_public.data,
                          project_type=int(form.project_type.data),
                          user_id=current_user.id)
        db.session.add(project)
        db.session.commit()
        flash('Added project \'{}\''. format(project.name))
        return redirect(url_for('main.index'))
    return render_template('projects/create_project.html',
                            title='Create new project',
                            form=form)
