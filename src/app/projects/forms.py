"""

app/projects/forms.py

written by: Oliver Cordes 2019-02-04
changed by: Oliver Cordes 2019-02-04

"""


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import Project


class CreateProjectForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    is_public = BooleanField('Public' )
    submit = SubmitField('Create')


    def validate_name(self, name):
        project = Project.query.filter_by(name=name.data).first()
        if project is not None:
            raise ValidationError('Please use a different project name.')
