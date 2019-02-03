"""

app/auth/email.py

written by: Oliver Cordes 2019-01-26
changed by: Oliver Cordes 2019-01-29

"""

from flask import render_template, current_app
#from flask_babel import _
from app.email import send_email



def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Rayqueue] Reset Your Password',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))



def send_email_verify_email(user):
    token = user.get_email_verify_token()
    send_email('[Rayqueue] Verify your email address',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/verify_email.txt',
                                         user=user, token=token),
               html_body=render_template('email/verify_email.html',
                                         user=user, token=token))
