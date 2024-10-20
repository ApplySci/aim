from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SubmitField
from wtforms.validators import DataRequired, Email


class AddUserForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    tournament = RadioField("Tournament", validators=[DataRequired()])
    role = RadioField(
        "Role",
        choices=[("admin", "Admin"), ("editor", "Editor"), ("scorer", "Scorer")],
        default="editor",
        validators=[DataRequired()],
    )
    submit = SubmitField("Add User")
