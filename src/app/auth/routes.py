"""

app/auth/routes.py

written by: Oliver Cordes 2019-01-26
changed by: Oliver Cordes 2019-02-02

"""

import os
from datetime import datetime

from flask import current_app, request, render_template, \
                  url_for, flash, redirect
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse


from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, EditProfileForm, \
                           UpdatePasswordForm, ResetPasswordRequestForm, \
                           ResetPasswordForm, AdminPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email, send_email_verify_email


APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@bp.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    # so at this point we need to check if we have
    # a clean installation, just ask for admin
    # credentials
    if User.query.count()==0:  # no users available
        form = AdminPasswordForm()
        if form.validate_on_submit():
            user = User(username='admin', email='')
            user.set_password(form.password.data)
            user.first_name = 'System'
            user.last_name = 'Administrator'
            user.is_active = True
            user.administrator = True
            db.session.add(user)
            db.session.commit()

            flash('Password for the administrator account is now set!')
            return redirect(url_for('auth.login'))

        flash('No users in database! Enter an administrator password!')
        return render_template('auth/admin_password.html',
            title='Set Administrator Password', form=form)
    else:
        # proceed with the normal login procedure
        form = LoginForm()

        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password')
                return redirect(url_for('auth.login'))
            if login_user(user, remember=form.remember_me.data):
                next_page = request.args.get('next')
                if not next_page or url_parse(next_page).netloc != '':
                    next_page = url_for('main.index')
                return redirect(next_page)
            else:
                flash('User account is not active!')
                return redirect(url_for('auth.login'))
        return render_template('auth/login.html', title='Sign In',
                                form=form,
                                rform=RegistrationForm(),
                                pform=ResetPasswordRequestForm(),
                                mode='login')


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    rform = RegistrationForm()
    if rform.validate_on_submit():
        user = User(username=rform.username.data,
                    email=rform.email.data,
                    first_name=rform.first_name.data,
                    last_name=rform.last_name.data)
        user.set_password(rform.password.data)
        db.session.add(user)
        db.session.commit()
        send_email_verify_email(user)
        flash('Congratulations, you are now a registered user! An email was sent for confirmation!')
        return redirect(url_for('auth.login'))

    # this is the case of an error!
    return render_template('auth/login.html', title='Sign In',
                            form=LoginForm(),
                            rform=rform,
                            pform=ResetPasswordRequestForm(),
                            mode='signup')


@bp.route('/update_password', methods=['POST'])
def update_password():
    #user = User.query.filter_by(username=username).first_or_404()

    form = EditProfileForm(current_user.username)
    pform=UpdatePasswordForm()


    if pform.validate_on_submit():
        current_user.set_password(pform.password.data)
        db.session.commit()
        flash('Your new password has been saved.')

    return redirect(url_for('auth.user', username=current_user.username))
    #return render_template('user.html', user=current_user, form=form, pform=pform)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    pform = ResetPasswordRequestForm()
    if pform.validate_on_submit():
        user = User.query.filter_by(email=pform.email.data).first()
        if user:
            send_password_reset_email(user)
            print(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))

    return render_template('auth/login.html', title='Sign In',
                            form=LoginForm(),
                            rform=RegistrationForm(),
                            pform=pform,
                            mode='reset')



@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@bp.route('/verify_email/<token>', methods=['GET','POST'])
def verify_email(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_email_verify_token(token)
    if not user:
        msg = 'No such user in token'
        current_app.logger.info(msg)
        flash(msg)
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()

    user.is_active = True
    db.session.commit()
    msg = 'Your account is now complete.'
    current_app.logger.info(msg)
    flash(msg)

    return redirect(url_for('auth.login'))
