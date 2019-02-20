"""

app/projects/forms.py

written by: Oliver Cordes 2019-02-04
changed by: Oliver Cordes 2019-02-20

"""


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, \
                    SubmitField, TextAreaField, RadioField, \
                    SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import Project


class CreateProjectForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    project_type = RadioField('Type', choices=[('0','Image'),('1','Animation')], validators=[DataRequired()])
    version = SelectField(u'Povray version', choices=[('3.7', '3.7'), ('3.8', '3.8'), ('3.6', '3.6')])
    is_public = BooleanField('Public' )
    submit = SubmitField('Create')


    def validate_name(self, name):
        project = Project.query.filter_by(name=name.data).first()
        if project is not None:
            raise ValidationError('Please use a different project name.')


class UpdateProjectForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    project_type = RadioField('Type', choices=[('0','Image'),('1','Animation')], validators=[DataRequired()])
    version = SelectField(u'Povray version', choices=[('3.7', '3.7'), ('3.8', '3.8'), ('3.6', '3.6')])
    is_public = BooleanField('Public' )

    update = SubmitField('Update')


class ProjectListForm(FlaskForm):
    remove = SubmitField('Remove')
    create = SubmitField('Create')
