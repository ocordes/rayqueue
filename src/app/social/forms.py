"""

app/social/forms.py

written by: Oliver Cordes 2020-03-18
changed by: Oliver Cordes 2020-03-28

"""


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, \
                    SubmitField, TextAreaField, RadioField, \
                    SelectField, IntegerField, HiddenField
from wtforms.widgets import HTMLString
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import ValidationError, DataRequired, \
                               Email, EqualTo, Length
from app.models import Project



class UploadFlickrForm(FlaskForm):
    imageid = HiddenField('imageid', id='upload_imageid', default=-1)
    upload = SubmitField('flickr upload')


class UploadPiwigoForm(FlaskForm):
    imageid = HiddenField('imageid', id='upload_imageid', default=-1)
    upload = SubmitField('Piwigo upload')


class AuthPiwigoForm(FlaskForm):
    host = StringField('Host URL', validators=[DataRequired()])
    username = StringField('UserName', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Authorize')
