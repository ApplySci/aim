# -*- coding: utf-8 -*-
"""
"""
from datetime import datetime

from flask_wtf import FlaskForm
import requests
from wtforms import DateTimeLocalField, RadioField, StringField, SubmitField, \
    ValidationError
from wtforms.validators import DataRequired, Optional, URL

def url_ok(form, field):
    try:
        response = requests.get(field.data)
        if response.status_code != 200:
            raise ValidationError('URL must be valid and return a 200 status code.')
    except requests.exceptions.RequestException:
        raise ValidationError('URL must be valid and return a 200 status code.')


def start_date_check(form, field):
    given_datetime = datetime(2024, 6, 14)  # replace with your datetime
    if field.data > given_datetime:
        raise ValidationError('Start date must be earlier than or equal to start of first hanchan:')

def end_date_check(form, field):
    given_datetime = datetime(2024, 6, 20)  # replace with your datetime
    if field.data < given_datetime:
        raise ValidationError('End date must be later than or equal to given datetime.')

class TournamentForm(FlaskForm):
    start_date = DateTimeLocalField(
        'Start Date', format='%Y-%m-%dT%H:%M',
        validators=[DataRequired(), start_date_check])
    end_date = DateTimeLocalField(
        'End Date', format='%Y-%m-%dT%H:%M',
        validators=[DataRequired(), end_date_check])
    address = StringField('Address', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    status = RadioField('Status', choices=[
        ('testing', 'Testing'), ('pending', 'Pending'), ('live', 'Live'),
        ('finished', 'Finished')
        ], validators=[DataRequired()])

    url = StringField('URL', validators=[Optional(), URL(), url_ok])
    url_icon = StringField('Icon URL', validators=[Optional(), URL(), url_ok])
    submit = SubmitField('Submit')
