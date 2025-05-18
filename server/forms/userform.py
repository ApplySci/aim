# -*- coding: utf-8 -*-
"""
User management form definitions.

Defines WTForms form classes for user management operations,
including adding users to tournaments and assigning roles.
"""

from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField
from wtforms.validators import DataRequired, Email
from forms.tournament_forms import GoogleAccountField


class AddUserForm(FlaskForm):
    email = GoogleAccountField(
        "Email (must be a google account)",
        validators=[DataRequired(), Email()],
    )
    role = RadioField(
        "Role",
        choices=[("admin", "Admin"), ("editor", "Editor"), ("scorer", "Scorer")],
        default="editor",
        validators=[DataRequired()],
    )
    submit = SubmitField("Add User")
