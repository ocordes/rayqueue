"""

app/projects/routes.py

written by: Oliver Cordes 2019-02-04
changed by: Oliver Cordes 2020-02-29

"""

import os
from datetime import datetime

from flask import current_app, request, render_template, \
                  url_for, flash, redirect, send_file, \
                  make_response, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename


from app import db
from app.projects import bp
from app.projects.forms import CreateProjectForm, UpdateProjectForm, \
                               ProjectListForm, \
                               ManageBaseFileForm, ManageImageForm
from app.projects.admin import owner_required, check_access
from app.models import User, Project, \
                        File, FILE_BASE_FILE, \
                        Image
#from app.auth.email import send_password_reset_email, send_email_verify_email

from app.utils.files import size2human
from app.utils.backref import get_redirect_target



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
                            title='Project \'{}\''.format(project.name),
                            form=form,
                            mform=ManageBaseFileForm(prefix='Manage'),
                            iform=ManageImageForm(prefix='Image'),
                            user=user,
                            readonly=user.id != project.user_id,
                            project=project,
                            size2human=size2human )


# upload_project_basefile
#
# adopted from:
# https://pythonise.com/categories/javascript/upload-progress-bar-xmlhttprequest

@bp.route('/project/basefile/<projectid>/add', methods=['POST'])
@login_required
@owner_required('projectid')
def upload_project_basefile(projectid):
    project = Project.query.get(projectid)
    user    = User.query.get(project.user_id)

    # get the file from the request
    f = request.files["file"]
    filename = secure_filename(f.filename)

    new_file = File.save_file(f, filename, FILE_BASE_FILE, project)

    db.session.add(new_file)
    db.session.commit()

    msg = 'Added \'{}\' to BaseFiles'.format(filename)

    res = make_response(jsonify({"message": msg}), 200)

    return res



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


@bp.route('/project/image/<projectid>/remove', methods=['POST'])
@login_required
@owner_required('projectid')
def remove_project_image(projectid):
    iform = ManageImageForm(prefix='Image')
    if iform.validate_on_submit():
        # get a list of selected items
        for id in request.form.getlist('images'):
            image = Image.query.get(id)
            ret, retmsg = image.remove()
            if ret:
                # image files were removed successfully
                # remove from database
                msg = 'Remove id=\'{}\' from Image'.format(id)
                db.session.delete(image)
            else:
                msg = 'Removing id=\'{}\' failed ({})'.format(id, retmsg)
            flash(msg)
            current_app.logger.info(msg)
        db.session.commit()
    return redirect(url_for('projects.show_project', projectid=projectid))



"""
get_project_file

provides the file with the original name (skipping the uuid-code!)
"""
@bp.route('/project/file/<projectid>/get/<fileid>', methods=['GET'])
@login_required
@owner_required('projectid')
def get_project_file(projectid,fileid):
    projectid = int(projectid)

    # look from which page we are called!
    target = get_redirect_target()

    project = Project.query.get(projectid)
    ffile = File.query.get(fileid)

    if ffile.project_id == projectid:
        filename = ffile.full_filename()
        orig_name = ffile.name[37:]
        return send_file(filename, as_attachment=True, attachment_filename=orig_name)
    else:
        msg = 'File doesn\'t match project ownership!'
        flash(msg)
        current_app.logger.info(msg)

    # back to caller
    return redirect(target)


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
            ret, msgs = project.remove_files()
            if ret:
                db.session.delete(project)
                msg = 'remove project name={}'.format(project.name)
                current_app.logger.info(msg)
            else:
                for msg in msgs:
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
        #return redirect(url_for('main.index'))
        # refer to the new created project
        return redirect(url_for('projects.show_project',projectid=project.id))
    elif request.method == 'GET':
        # this is necessary, since WTF RadioField has no
        # default values ...
        form.project_type.default = str(0)
        form.process()
    return render_template('projects/create_project.html',
                            title='Create new project',
                            form=form)
