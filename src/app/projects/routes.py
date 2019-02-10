"""

app/projects/routes.py

written by: Oliver Cordes 2019-02-04
changed by: Oliver Cordes 2019-02-10

"""

import os
from datetime import datetime

from flask import current_app, request, render_template, \
                  url_for, flash, redirect
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse


from app import db
from app.projects import bp
from app.projects.forms import CreateProjectForm, UpdateProjectForm, \
                               ProjectListForm
from app.projects.admin import owner_required, check_access
from app.models import User, Project
#from app.auth.email import send_password_reset_email, send_email_verify_email




@bp.route('/project/<projectid>', methods=['GET','POST'])
@owner_required('projectid')
@login_required
def show_project(projectid):
    form = UpdateProjectForm()

    project = Project.query.get(projectid)
    user    = User.query.get(project.user_id)

    if form.validate_on_submit():
        project.name = form.name.data
        project.is_public=form.is_public.data
        project.project_type=int(form.project_type.data)
        db.session.commit()
        flash('Your changes have been saved.')
    elif request.method == 'GET':
        form.name.default = project.name
        form.project_type.default = str(project.project_type)
        form.is_public.default = project.is_public
        form.process()

    return render_template('projects/show_project.html',
                            title='Project',
                            form=form,
                            user=user,
                            project=project)


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
    form = ProjectListForm()
    if form.validate_on_submit():
        if form.create.data:
            return redirect(url_for('projects.create_project'))

        # get a list of selected items
        selected_projects = request.form.getlist('projects')
        for id in selected_projects:
            project = Project.query.get(id)
            db.session.delete(project)
            msg = 'remove project name={}'.format(project.name)
            flash(msg)
            current_app.logger.info(msg)
        db.session.commit()
        return redirect(url_for('projects.show_projects'))

    return render_template('projects/show_projects.html',
                            title='Project list',
                            projects=projects,
                            user_id=User.query.get,
                            form=form)


@bp.route('/create_project', methods=['GET','POST'])
@login_required
def create_project():
    form = CreateProjectForm()

    if form.validate_on_submit():
        project = Project(name=form.name.data,
                          is_public=form.is_public.data,
                          project_type=int(form.project_type.data),
                          user_id=current_user.id,
                          status=0)
        db.session.add(project)
        db.session.commit()
        flash('Added project \'{}\''. format(project.name))
        return redirect(url_for('main.index'))
    elif request.method == 'GET':
        # this is necessary, since WTF RadioField has no
        # default values ...
        form.project_type.default = str(0)
        form.process()
    return render_template('projects/create_project.html',
                            title='Create new project',
                            form=form)
