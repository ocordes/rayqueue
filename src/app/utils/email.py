"""

app/utils/email.py

written by: Oliver Cordes 2019-01-26
changed by: Oliver Cordes 2019-02-24

"""


from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail


def send_async_email(app, msg, subject, recipients):
    txtmsg = 'Message sent to: {} \'{}\''.format(recipients, subject)
    with app.app_context():
        mail.send(msg)
        current_app.logger.info(txtmsg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg, subject, recipients)).start()
