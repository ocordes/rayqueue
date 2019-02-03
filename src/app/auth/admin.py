"""

app/auth/admin.py

written by: Oliver Cordes 2019-02-03
changed by: Oliver Cordes 2019-02-03

"""


from flask import current_app, url_for, flash, redirect
from flask_login import current_user

from functools import wraps


def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.administrator:
            return f(*args, **kwargs)
        else:
            flash('You need administrator rights to access this page!')
            return redirect(url_for('main.index'))
    return wrap
