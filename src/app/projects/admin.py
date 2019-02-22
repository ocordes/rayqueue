"""

app/projects/admin.py

written by: Oliver Cordes 2019-02-07
changed by: Oliver Cordes 2019-02-22

"""


from flask import current_app, request, url_for, flash, redirect
from flask_login import current_user

from functools import wraps

from app.models import User, Project


def check_access(user, project):
    if user.is_anonymous:
        return False, 'Anonymous user'
    if user.administrator:
        return True, 'Administrator'
    if user.id == project.user_id:
        return True, 'Owner'
    if project.is_public:
        return True, 'Public project'
    return  False, 'Private project, not owner'


def owner_required(keyword):
    def real_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            fail = False
            data = kwargs[keyword]
            if data is None:
                flash('Keyword in \'owner_required\' created no data!')
                fail = True
            else:
                project = Project.query.get(int(data))

                ret, msg = check_access(current_user, project)
                fail = not ret

            if fail:
                flash('You are not owner of this project!')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return wrapper
    return real_decorator
