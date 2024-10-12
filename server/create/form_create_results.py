# -*- coding: utf-8 -*-
"""
@author: ZAPS@mahjong.ie
"""
import pytz
import re
import os

from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import (
    DataRequired,
    Email,
    NumberRange,
    Optional,
    ValidationError,
    Regexp,
)


class GameParametersForm(FlaskForm):

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

    timezone = SelectField(
        "Timezone",
        choices=[(tz, tz) for tz in pytz.common_timezones],
        default="Europe/Dublin",
    )
    table_count = IntegerField(
        "Number of tables (players divided by 4) [2-43]",
        default=10,
        validators=[DataRequired(), NumberRange(min=2, max=43)],
    )
    hanchan_count = IntegerField(
        "Number of hanchan [2-15]",
        default=7,
        validators=[DataRequired(), NumberRange(min=2, max=15)],
    )
    title = StringField(
        "Spreadsheet Title",
        default="Riichi Tournament Scoresheet",
        validators=[DataRequired()],
    )
    notify = BooleanField(
        "Notify the scorer as soon as the scoresheet has been created",
        default=True,
    )
    emails = StringField(
        "Scorer's email address",
        validators=[
            Optional(),
            Email(),
        ],
    )
    submit = SubmitField("Create the google sheet")

    web_directory = StringField(
        "Tournament short name (for URLs)",
        validators=[
            DataRequired(),
            Regexp(
                r"^[-_a-z0-9]+$",
                message="Only lowercase letters, numbers, hyphens, and underscores are allowed.",
            ),
        ],
    )

    @staticmethod
    def validate_web_directory(form, field):
        directory_path = os.path.join("./static", field.data)
        if os.path.exists(directory_path) and os.listdir(directory_path):
            raise ValidationError(
                "This directory already exists and is not empty. Please choose a different name."
            )
