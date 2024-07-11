# -*- coding: utf-8 -*-
"""
@author: ZAPS@mahjong.ie
"""
import pytz

from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, SelectField, StringField, \
    SubmitField
from wtforms.validators import DataRequired, Email, NumberRange, Optional, \
    ValidationError


class FirebaseDataForm(FlaskForm):
    """
    address : str
    country : str
    name : str
    rules : str default: "EMA RCR" / "WRC" / freeform
    start_date : DateTime with timezone
    end_date : DateTime with timezone
    status : str "live"
    url_icon : str
    url : str
    """
    pass


class GameParametersForm(FlaskForm):

    hanchan_name = SelectField(
        'What name should be used for tournament rounds?',
        choices=[
            ('Round ?', 'Round ?'),
            ('Hanchan ?', 'Hanchan ?'),
            ('Game ?', 'Game ?'),
            ('other', 'Custom (please specify)'),
            ])
    other_name = StringField('Custom name', render_kw={'disabled': ''})

    @staticmethod
    def validate_other_name(form, field):
        if form.hanchan_name.data == 'other':
            if not field.data:
                raise ValidationError(
                    'This field is required when "Other" is selected in Choice Field',
                    );
            if '?' not in field.data:
                raise ValidationError('Missing the "?" placeholder');

    timezone = SelectField(
        'Timezone',
        choices=[(tz, tz) for tz in pytz.common_timezones],
        default='Europe/Dublin',
        )
    table_count = IntegerField(
        'Number of tables [4-20] (players divided by 4)',
        default = 10,
        validators=[DataRequired(), NumberRange(min=4, max=20)])
    hanchan_count = IntegerField(
        'Number of hanchan [1-20]',
        default = 7,
        validators=[DataRequired(), NumberRange(min=1, max=20)])
    title = StringField('Spreadsheet Title',
                        default = 'Riichi Tournament Scoresheet',
                        validators=[DataRequired()],
                        )
    notify = BooleanField(
        'Notify the scorer as soon as the scoresheet has been created',
        default = True,
        )
    emails = StringField("Scorer's email address", validators=[
        Optional(),
        Email(),
        ])
    submit = SubmitField('Create the google sheet')
