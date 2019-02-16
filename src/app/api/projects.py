"""

api/projects.py

written by: Oliver Cordes 2019-02-11
changed by: Oliver Cordes 2019-02-14

"""


from datetime import datetime

from flask import current_app, make_response, abort, jsonify

from flask_login import current_user, login_user, logout_user, login_required

from app import db
from app.api import bp

from app.models import User, Project

from app.api.checks import body_get


"""
find_project


:param user: user_id from token
:param token_info: info of the token
:rvalue: returns an array of all projects with user_id as owner
"""
def find_projects(user, token_info):
    u = User.query.get(int(user))

    data = [p.to_dict() for p in u.projects.all()]

    return jsonify(data)



"""
add_project

:param user: user_id from token
:param token_info: info of the token
:param body: the json dictonary of the request
"""
def add_project(user, token_info, body):
    print(user)
    print(body)

    name = body_get(body, 'name')
    is_public = body_get(body, 'is_public')
    project_type = body_get(body, 'project_type')

    project = Project.query.filter_by(name=name).first()
    if project is not None:
        abort( 400,
               'Project with name={} already exists'.format(name) )

    project = Project(name=body.get('name', 'Some project'),
                    is_public=body.get('is_public', False),
                    user_id=user,
                    project_type=body.get('project_type',0),
                    status=0)

    db.session.add(project)
    db.session.commit()

    return jsonify(project.to_dict())


"""
get_project
"""

def get_project(user, token_info, project_id):
    project = Project.query.get(project_id)

    if project is None:
        abort(404, 'No project with such id')

    if project.user_id != user:
        abort(401, 'You are not the owner of this project')

    return jsonify(project.to_dict())


"""
update_project
"""

def update_project(user, token_info, project_id, body):
    print(user)
    print(body)
    project = Project.query.get(project_id)

    if project is None:
        abort(404, 'No project with such id')

    if project.user_id != user:
        abort(401, 'You are not the owner of this project')


    return jsonify(project.to_dict())



"""
remove_project
"""

def remove_project(user, token_info, project_id):
    project = Project.query.get(project_id)

    if project is None:
        abort(404, 'No project with such id')

    if project.user_id != user:
        abort(401, 'You are not the owner of this project')

    return jsonify(project.to_dict())
