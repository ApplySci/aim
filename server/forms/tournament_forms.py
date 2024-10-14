from datetime import datetime
import os

from flask_wtf import FlaskForm
import pycountry
import pytz
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

BASEDIR = "/home/model/apps/tournaments/static/"
ALLOWED_TAGS = [
    "p", "b", "i", "h1", "h2", "h3", "a", "br", "strong", "em", "u", "ol", "ul", "li",
]


def url_ok(form, field):
    if field.data == "":
        return
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(field.data, headers=headers)
        if response.status_code >= 400:
            raise ValidationError(
                f"Error {response.status_code}: " "URL must be valid and reachable"
            )
    except requests.exceptions.RequestException:
        raise ValidationError("URL must be valid and reachable")


def start_date_check(custom_start_date):
    def _start_date_check(form, field):
        if datetime.strptime(custom_start_date, "%A %d %B %Y, %H:%M") < field.data:
            print("failed start date validation")
            raise ValidationError(
                "Start date must be earlier than or equal to start of first hanchan:"
            )

    return _start_date_check


def end_date_check(custom_end_date):
    def _end_date_check(form, field):
        if datetime.strptime(custom_end_date, "%A %d %B %Y, %H:%M") >= field.data:
            raise ValidationError(
                "End date must be later than the start of the last hanchan."
            )

    return _end_date_check


def validate_google_doc_id(form, field):
    try:
        googlesheet.get_sheet(field.data)
    except Exception:
        raise ValidationError("Invalid Google Doc ID or insufficient permissions.")


def validate_web_directory(form, field):
    directory_path = os.path.join(BASEDIR, field.data)
    if os.path.exists(directory_path) and any(
        os.path.isfile(os.path.join(directory_path, entry))
        for entry in os.listdir(directory_path)
    ):
        raise ValidationError(
            "This directory already exists and is not empty. Please choose a different name."
        )

class TournamentFormBase(FlaskForm):
    name = StringField("Tournament Name", validators=[DataRequired()])
    start_date = DateTimeLocalField("Start Date", format="%Y-%m-%dT%H:%M")
    end_date = DateTimeLocalField("End Date", format="%Y-%m-%dT%H:%M")
    address = StringField("Address", validators=[DataRequired()])
    countries = sorted(
        [(country.alpha_2, country.name) for country in pycountry.countries],
        key=lambda e: e[1],
    )
    country = SelectField("Country", choices=countries)
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
    url = StringField("Tournament URL", validators=[Optional(), URL(), url_ok])
    url_icon = StringField("Icon URL", validators=[Optional(), URL(), url_ok])
    google_doc_id = StringField(
        "Google Doc ID", validators=[DataRequired(), validate_google_doc_id]
    )
    web_directory = StringField(
        "Web Directory", validators=[DataRequired(), validate_web_directory]
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
    timezone = SelectField(
        "Timezone",
        choices=[(tz, tz) for tz in pytz.common_timezones],
        default="Europe/Dublin",
    )
    round_dates = FieldList(DateTimeLocalField("Round Date/Time"), min_entries=0)

    submit = SubmitField("Submit")

    def set_round_dates(self, data):
        while len(self.round_dates) > 0:
            self.round_dates.pop_entry()
        for date in data:
            self.round_dates.append_entry(date)
