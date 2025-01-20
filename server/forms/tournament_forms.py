# -*- coding: utf-8 -*-
"""
Tournament-related form definitions.

Defines WTForms form classes for tournament creation and management,
including validation rules for dates, URLs, and other tournament parameters.
Includes custom validators for ensuring data integrity and accessibility.
"""
from datetime import datetime
import os

from config import BASEDIR
from flask_wtf import FlaskForm
import pycountry
import requests
from wtforms import (
    BooleanField,
    DateTimeLocalField,
    IntegerField,
    RadioField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
    FieldList,
)
from wtforms.validators import (
    DataRequired,
    Email,
    NumberRange,
    Optional,
    URL,
    ValidationError,
    Regexp,
)

from write_sheet import googlesheet

ALLOWED_TAGS = [
    "p",
    "b",
    "i",
    "h1",
    "h2",
    "h3",
    "a",
    "br",
    "strong",
    "em",
    "u",
    "ol",
    "ul",
    "li",
]


def url_ok(form, field):
    if field.data:
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(field.data, headers=headers)
            if response.status_code >= 400:
                raise ValidationError("URL must be valid and reachable")
        except requests.exceptions.RequestException:
            raise ValidationError("URL must be valid and reachable")


def validate_start_date(form, field):
    if form.custom_start_date and form.custom_start_date < field.data:
        raise ValidationError(
            "Start date must be earlier than or equal to start of first hanchan"
        )


def validate_end_date(form, field):
    if form.custom_end_date and form.custom_end_date >= field.data:
        raise ValidationError(
            "End date must be later than the start of the last hanchan."
        )


def validate_google_doc_id(form, field):
    try:
        googlesheet.get_sheet(field.data)
    except Exception:
        raise ValidationError("Invalid Google Doc ID or insufficient permissions.")


def validate_web_directory(form, field):
    if not hasattr(form, "is_edit") or not form.is_edit:
        directory_path = os.path.join(BASEDIR, field.data)
        if os.path.exists(directory_path) and any(
            os.path.isfile(os.path.join(directory_path, entry))
            for entry in os.listdir(directory_path)
        ):
            raise ValidationError(
                "This directory already exists and is not empty. Please choose a different name."
            )


def validate_other_name(form, field):
    if form.hanchan_name.data == "other":
        if not field.data:
            raise ValidationError(
                'This field is required when "Other" is selected in Choice Field'
            )
        if "?" not in field.data:
            raise ValidationError('Missing the "?" placeholder')


class TournamentForm(FlaskForm):
    title = StringField(
        "Tournament name",
        default="World Riichi League",
        validators=[DataRequired()],
    )
    start_date = DateTimeLocalField(
        "Start Date",
        format="%Y-%m-%dT%H:%M",
        validators=[Optional(), validate_start_date],
    )
    end_date = DateTimeLocalField(
        "End Date",
        format="%Y-%m-%dT%H:%M",
        validators=[Optional(), validate_end_date],
    )
    address = StringField(
        "Address (this will be used as a lookup string for google maps)",
        validators=[Optional()],
    )

    countries = sorted(
        [(country.alpha_2, country.name) for country in pycountry.countries],
        key=lambda e: e[1],
    )
    country = SelectField("Country", choices=countries, default="DE")
    timezone = SelectField(
        "Timezone",
        choices=[],  # Remove default choices
        validators=[DataRequired()]
    )

    status = RadioField(
        "Status",
        choices=[
            ("upcoming", "Upcoming"),
            ("live", "Live"),
            ("past", "Finished"),
            ("test", "Testing"),
        ],
        default="upcoming",
        validators=[DataRequired()],
    )
    rules = RadioField(
        "Rules",
        default="WRC",
        choices=[("WRC", "WRC"), ("EMA", "EMA"), ("custom", "custom")],
        validators=[DataRequired()],
    )
    url = StringField(
        "Tournament URL",
        default="https://worldriichileague.com/",
        validators=[Optional(), URL(), url_ok],
    )
    url_icon = StringField("Icon URL", validators=[Optional(), URL(), url_ok])
    google_doc_id = StringField(
        "Google Doc ID", validators=[Optional(), validate_google_doc_id]
    )
    web_directory = StringField(
        "Short name (for URLs), 3-20 characters; use only -_a-z0-9",
        validators=[
            DataRequired(),
            validate_web_directory,
            Regexp(
                r"^[-_a-z0-9]+$",
                message="3-20 characters: only letters, numbers, hyphens, and underscores are allowed",
            ),
        ],
    )
    htmlnotes = TextAreaField(
        f'HTML Notes (tags allowed: {", ".join(ALLOWED_TAGS)})', validators=[Optional()]
    )

    # Fields specific to tournament creation
    table_count = IntegerField(
        "Number of tables (players divided by 4) [4-43]",
        default=10,
        validators=[DataRequired(), NumberRange(min=4, max=43)],
    )
    hanchan_count = IntegerField(
        "Number of hanchan [2-15]",
        default=7,
        validators=[DataRequired(), NumberRange(min=2, max=15)],
    )
    round_dates = FieldList(DateTimeLocalField("Round Date/Time"), min_entries=0)

    hanchan_name = SelectField(
        "What name should be used for tournament rounds?",
        choices=[
            ("Round ?", "Round ?"),
            ("Hanchan ?", "Hanchan ?"),
            ("Game ?", "Game ?"),
            ("other", "Custom (please specify)"),
        ],
    )
    other_name = StringField(
        "Custom round name",
        render_kw={"readonly": ""},
        validators=[validate_other_name],
    )
    notify = BooleanField(
        "Notify the scorer as soon as the scoresheet has been created",
        default=True,
    )
    scorer_emails = FieldList(
        StringField(
            "Additional Scorer Emails",
            validators=[Optional(), Email()],
        ),
        min_entries=1,
    )
    use_winds = BooleanField(
        "Use the winds as assigned in the pre-defined seating",
        default=False,
    )

    submit = SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        self.is_edit = kwargs.pop("is_edit", False)
        self.custom_start_date = kwargs.pop("custom_start_date", None)
        self.custom_end_date = kwargs.pop("custom_end_date", None)
        super(TournamentForm, self).__init__(*args, **kwargs)

    def set_round_dates(self, data):
        while len(self.round_dates) > 0:
            self.round_dates.pop_entry()
        for date in data:
            self.round_dates.append_entry(date)

    @property
    def round_labels(self):
        template = (
            self.other_name.data
            if self.hanchan_name.data == "other"
            else self.hanchan_name.data
        )
        return [template.replace("?", str(i + 1)) for i in range(len(self.round_dates))]


class EditTournamentForm(TournamentForm):
    class Meta:
        # List of fields to include
        include = [
            "title",
            "start_date",
            "end_date",
            "address",
            "country",
            "status",
            "rules",
            "url",
            "url_icon",
            "google_doc_id",
            "web_directory",
            "htmlnotes",
            "submit",
        ]

    def __init__(self, *args, **kwargs):
        super(EditTournamentForm, self).__init__(*args, **kwargs)
        # Remove validators from fields that shouldn't be validated during edit
        self.google_doc_id.validators = [Optional()]
        self.web_directory.validators = [
            DataRequired(),
            Regexp(
                r"^[-_a-zA-Z0-9]+$",
                message="Only letters, numbers, hyphens, and underscores are allowed",
            ),
        ]

        # Remove fields that are not needed for editing
        del self.hanchan_name
        del self.other_name
        del self.table_count
        del self.hanchan_count
        del self.timezone
        del self.round_dates
        del self.notify
        del self.scorer_emails
