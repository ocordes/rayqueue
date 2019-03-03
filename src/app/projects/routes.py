"""

app/projects/routes.py

written by: Oliver Cordes 2019-02-04
changed by: Oliver Cordes 2019-03-03

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
                               ManageBaseFileForm
from app.projects.admin import owner_required, check_access
from app.models import User, Project, File, \
                       FILE_BASE_FILE
#from app.auth.email import send_password_reset_email, send_email_verify_email

from app.utils.files import size2human



@bp.route('/project/<projectid>', methods=['GET','POST'])
@login_required
@owner_required('projectid')
def show_project(projectid):
    form = UpdateProjectForm(prefix='Update')

    project = Project.query.get(projectid)
    user    = User.query.get(project.user_id)


    if form.validate_on_submit():
        project.name = form.name.data
        project.is_public = form.is_public.data
        project.project_type = int(form.project_type.data)
        project.version = form.version.data
        db.session.commit()
        flash('Your changes have been saved.')
    else:
        form.name.default = project.name
        form.project_type.default = str(project.project_type)
        form.version.default = project.version
        form.is_public.default = project.is_public
        form.process()

    return render_template('projects/show_project.html',
                            title='Project',
                            form=form,
                            uform=UploadBaseFilesForm(prefix='Upload'),
                            mform=ManageBaseFileForm(prefix='Manage'),
                            user=user,
                            readonly=user.id != project.user_id,
                            project=project,
                            size2human=size2human )


@bp.route('/project/basefile/<projectid>/add', methods=['POST'])
@login_required
@owner_required('projectid')
def upload_project_basefile(projectid):
    form = UploadBaseFilesForm(prefix='Upload')

    project = Project.query.get(projectid)
    user    = User.query.get(project.user_id)

    if form.validate_on_submit():

        f = form.upload.data
        filename = secure_filename(f.filename)
        new_file = File.save_file(f, filename, FILE_BASE_FILE, project)

        db.session.add(new_file)
        db.session.commit()

        msg = 'Added \'{}\' to BaseFiles'.format(filename)
        flash(msg)
        current_app.logger.info(msg)
    return redirect(url_for('projects.show_project', projectid=projectid))


@bp.route('/project/basefile/<projectid>/remove', methods=['POST'])
@login_required
@owner_required('projectid')
def remove_project_basefile(projectid):
    mform = ManageBaseFileForm(prefix='Manage')
    if mform.validate_on_submit():
        # get a list of selected items
        #selected_files = request.form.getlist('files')
        for id in request.form.getlist('files'):
            fid = File.query.get(id)
            ret, retmsg = fid.remove()
            if ret:
                # file was remove successfully
                # remove from database
                msg = 'Remove \'{}\' from BaseFiles'.format(fid.name)
                db.session.delete(fid)
            else:
                msg = 'Removing \'{}\' failed ({})'.format(fid.name, retmsg)
            flash(msg)
            current_app.logger.info(msg)
        db.session.commit()
    return redirect(url_for('projects.show_project', projectid=projectid))


@bp.route('/project/basefile/<projectid>/get/<fileid>', methods=['GET'])
@login_required
@owner_required('projectid')
def get_project_basefile(projectid,fileid):
    projectid = int(projectid)
    print(projectid)
    print(fileid)

    project = Project.query.get(projectid)
    ffile = File.query.get(fileid)
    print(ffile.project_id)
    print(type(projectid))
    if ffile.project_id == projectid:
        filename = ffile.full_filename()
        orig_name = ffile.name[37:]
        return send_file(filename, as_attachment=True, attachment_filename=orig_name)
    else:
        msg = 'File doesn\'t match project ownership!'
        flash(msg)
        current_app.logger.info(msg)
    return redirect(url_for('projects.show_project', projectid=projectid))


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


@bp.route('/project/add', methods=['GET','POST'])
@login_required
def create_project():
    form = CreateProjectForm()

    if form.validate_on_submit():
        project = Project(name=form.name.data,
                          is_public=form.is_public.data,
                          project_type=int(form.project_type.data),
                          version=form.version.data,
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
