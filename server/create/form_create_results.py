# -*- coding: utf-8 -*-
"""
Fields for creating a new tournament
"""
import pytz
import re
import os

from flask_wtf import FlaskForm
from forms.tournament_forms import TournamentFormBase
from wtforms import SelectField, StringField
from wtforms.validators import ValidationError


class GameParametersForm(TournamentFormBase):

    hanchan_name = SelectField(
        "What name should be used for tournament rounds?",
        choices=[
            ("Round ?", "Round ?"),
            ("Hanchan ?", "Hanchan ?"),
            ("Game ?", "Game ?"),
            ("other", "Custom (please specify)"),
        ],
    )
    other_name = StringField("Custom round name", render_kw={"readonly": ""})

    @staticmethod
    def validate_other_name(form, field):
        if form.hanchan_name.data == "other":
            if not field.data:
                raise ValidationError(
                    'This field is required when "Other" is selected in Choice Field',
                )
            if "?" not in field.data:
                raise ValidationError('Missing the "?" placeholder')

    @property
    def round_labels(self):
        template = (
            self.other_name.data
            if self.hanchan_name.data == "other"
            else self.hanchan_name.data
        )
        return [template.replace("?", str(i + 1)) for i in range(len(self.round_dates))]
