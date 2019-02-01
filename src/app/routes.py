"""

app/routes.py

written by: Oliver Cordes 2019-01-26
changed by: Oliver Cordes 2019-01-30

"""


from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, UpdatePasswordForm, ResetPasswordRequestForm, ResetPasswordForm, AdminPasswordForm
from app.models import User

from app.email import send_password_reset_email, send_email_verify_email

import os

from flask import request, render_template, url_for, flash, redirect, send_from_directory, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


"""
before_request will be executed before any page will be
rendered
"""
@app.app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'Miguel'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', posts=posts)


@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

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
            return redirect(url_for('login'))

        flash('No users in database! Enter an administrator password!')
        return render_template('admin_password.html',
            title='Set Administrator Password', form=form)
    else:
        # proceed with the normal login procedure
        form = LoginForm()

        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password')
                return redirect(url_for('login'))
            if login_user(user, remember=form.remember_me.data):
                next_page = request.args.get('next')
                if not next_page or url_parse(next_page).netloc != '':
                    next_page = url_for('index')
                return redirect(next_page)
            else:
                flash('User account is not active!')
                return redirect(url_for('login'))
        return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        db.session.add(user)
        db.session.commit()
        send_email_verify_email(user)
        flash('Congratulations, you are now a registered user! An email was sent for confirmation!')
        return redirect(url_for('login'))


    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>', methods=['GET','POST'])
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
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email

    return render_template('user.html', user=user, form=form, pform=UpdatePasswordForm())


@app.route('/update_password', methods=['POST'])
def update_password():
    #user = User.query.filter_by(username=username).first_or_404()

    form = EditProfileForm(current_user.username)
    pform=UpdatePasswordForm()


    if pform.validate_on_submit():
        current_user.set_password(pform.password.data)
        db.session.commit()
        flash('Your new password has been saved.')

    return redirect(url_for('user', username=current_user.username))
    #return render_template('user.html', user=current_user, form=form, pform=pform)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/verify_email/<token>', methods=['GET','POST'])
def verify_email(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_email_verify_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()

    user.is_active = True
    db.session.commit()
    flash('Your account is now complete.')

    return redirect(url_for('login'))



@app.route("/upload", methods=['POST'])
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


@app.route('/api', methods=['POST'])
def api():
    return jsonify(username='hello',
                   email='president@whitehouse.gov',
                   id=42)
