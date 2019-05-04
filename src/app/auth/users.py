"""

app/auth/users.py

written by: Oliver Cordes 2019-02-03
changed by: Oliver Cordes 2019-02-10

"""


from flask import current_app, request, render_template, \
                  url_for, flash, redirect
from flask_login import current_user, login_required

from sqlalchemy import desc

from app import db
from app.auth import bp
from app.models import User, Project, HostInfo

from app.auth.forms import UserListForm, EditProfileForm, UpdatePasswordForm


from app.auth.admin import admin_required



@bp.route('/users', methods=['GET','POST'])
@login_required
@admin_required
def users():
    form = UserListForm()
    if form.validate_on_submit():
        # get a list of selected items
        selected_users = request.form.getlist("users")

        for uid in selected_users:
            # skip admin account
            if uid == '1':
                continue
            user = User.query.get(int(uid))
            # sets admin role
            if form.set_admin.data:
                if not user.administrator:
                    msg = 'set admin for user={} ({})'.format(uid,user.username)
                    current_app.logger.info(msg)
                    user.administrator = True
                    flash(msg)
            # clear admin role
            elif form.clear_admin.data:
                if user.administrator:
                    msg = 'clear admin for user={} ({})'.format(uid,user.username)
                    current_app.logger.info(msg)
                    user.administrator = False
                    flash(msg)
            # remove account
            elif form.remove.data:
                db.session.delete(user)
                msg = 'remove account user={} ({})'.format(uid,user.username)
                current_app.logger.info(msg)
                flash(msg)

        db.session.commit()
    return render_template('auth/users.html',
        title='List of users', users=User.query.all(), form=form)


@bp.route('/user/<username>', methods=['GET','POST'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()

    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('auth.user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
        print(user.projects.all())

    return render_template('auth/user.html',
                            user=user,
                            form=form,
                            projects=user.projects.all(),
                            pform=UpdatePasswordForm())


@bp.route('/workers', methods=['GET','POST'])
@login_required
@admin_required
def workers():
    workers = HostInfo.query.order_by(desc(HostInfo.active)).all()
    return render_template('auth/workers.html',
                            workers=workers)
