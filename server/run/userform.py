from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email

class AddUserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    tournament = SelectField('Tournament', coerce=str, validators=[DataRequired()])
    role = RadioField('Role', choices=[('admin', 'Admin'), ('editor', 'Editor')],
                      default="editor", validators=[DataRequired()])
    submit = SubmitField('Add User')