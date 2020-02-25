"""

app/main/routes.py

written by: Oliver Cordes 2019-01-26
changed by: Oliver Cordes 2020-02-25

"""

import os
from datetime import datetime

from flask import request, render_template, url_for, flash, redirect, send_from_directory, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse


from app import db
from app.main import bp
from app.models import *



APP_ROOT = os.path.dirname(os.path.abspath(__file__))


"""
before_request will be executed before any page will be
rendered
"""
@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return render_template('index.html', title='Dashboard')


@bp.route("/upload", methods=['POST'])
def upload():
    target = os.path.join(APP_ROOT, 'images/')
    print(target)

    if not os.path.isdir(target):
        os.mkdir(target)

    for file in request.files.getlist("file"):
        print(file)
        filename = file.filename
        destination = "/".join([target, filename])
        print(destination)
        file.save(destination)

    return render_template("complete.html")


"""
server_time

simple AJAX test
"""
@bp.route("/ajax/server_time", methods=['GET'])
def server_time():
    return datetime.utcnow().strftime('%H:%M:%S')


@bp.route('/ajax/running_data')
@login_required
def running_data():
    all_projects = Project.query.filter(Project.status==Project.PROJECT_RENDERING).all()

    projects = []
    for project in all_projects:
        if current_user.administrator == False:
            if project.user_id != current_user.id:
                if project.is_public == False:
                    continue
        projects.append(project)

    all_qes = QueueElement.query.all()

    qes = []
    for qe in all_qes:
        project = Project.query.get(qe.project)
        if current_user.administrator == False:
            if project.user_id != current_user.id:
                if project.is_public == False:
                    continue
        qes.append(qe)



    # look for the last image, which is finished and without error!
    index = 0
    last_image = -1
    for image in current_user.images:
        if image.render_image != -1:
            last_image = index
        index += 1

    if last_image != -1:
        imageid = current_user.images[last_image].id

        last_image_link = url_for('projects.get_render_image',imageid=imageid)
        last_image_src  = url_for('projects.get_render_icon',imageid=imageid)
        last_image_time = current_user.images[last_image].finished.strftime('%Y-%m-%d %H:%M:%S')
    else:
        last_image_link = ''
        last_image_src  = ''
        last_image_time = 'N/A'

    data = { 'projects': render_template('ajax/running_projects.html',
                    projects=projects),
             'queue': render_template('ajax/running_queue.html', qes=qes),
             'last_image_link': last_image_link,
             'last_image_src' : last_image_src,
             'last_image_time': last_image_time,
           }


    return jsonify(data)



@bp.route('/ajax/check_update')
@login_required
def check_update():
    is_update = False
    return jsonify( {'update' : is_update })
