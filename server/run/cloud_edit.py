# -*- coding: utf-8 -*-
"""
TODO get tournament hanchan times, and timezone, from googlesheet

"""
from datetime import datetime
import os

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
import pycountry
import requests

from wtforms import DateTimeLocalField, RadioField, SelectField, StringField, \
    SubmitField
from wtforms.validators import DataRequired, Optional, URL, ValidationError

from write_sheet import googlesheet
from oauth_setup import db, firestore_client

blueprint = Blueprint('edit', __name__)


def url_ok(form, field):
    if field.data == "":
        return
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(field.data, headers=headers)
        if response.status_code >= 400:
            raise ValidationError(f"Error {response.status_code}: "
                                  "URL must be valid and reachable")
    except requests.exceptions.RequestException:
        raise ValidationError('URL must be valid and reachable')


def start_date_check(custom_start_date):
    def _start_date_check(form, field):
        if datetime.strptime(custom_start_date, "%A %d %B %Y, %H:%M") \
            < field.data:
            print('failed start date validation')
            raise ValidationError('Start date must be earlier than or equal to start of first hanchan:')
    return _start_date_check


def end_date_check(custom_end_date):
    def _end_date_check(form, field):
        if datetime.strptime(custom_end_date, "%A %d %B %Y, %H:%M") \
            >= field.data:
            raise ValidationError('End date must be later than the start of the last hanchan.')
    return _end_date_check


def validate_google_doc_id(form, field):
    try:
        googlesheet.get_sheet(field.data)
    except Exception:
        raise ValidationError('Invalid Google Doc ID or insufficient permissions.')


def validate_web_directory(form, field):
    full_path = os.path.join('/home/model', field.data)
    if not os.path.isdir(full_path):
        raise ValidationError('Invalid directory path.')


class TournamentForm(FlaskForm):

    def __init__(self, custom_start_date, custom_end_date, *args, **kwargs):
      super(TournamentForm, self).__init__(*args, **kwargs)
      self.start_date.validators = [
          DataRequired(),
          start_date_check(custom_start_date),
          ]
      self.end_date.validators = [
          DataRequired(),
          end_date_check(custom_end_date),
          ]

    start_date = DateTimeLocalField('Start Date', format='%Y-%m-%dT%H:%M')
    end_date = DateTimeLocalField('End Date', format='%Y-%m-%dT%H:%M')

    address = StringField('Address', validators=[DataRequired()])
    countries = sorted([(country.alpha_2, country.name) \
                       for country in pycountry.countries],
                       key= lambda e:e[1])
    country = SelectField('Country', choices=countries)
    name = StringField('Name', validators=[DataRequired()])
    status = RadioField('Status', choices=[
        ('upcoming', 'Upcoming'), ('live', 'Live'),
        ('past', 'Finished'), ('test', 'Testing')
        ], default='upcoming', validators=[DataRequired()])

    rules = RadioField('Rules', default='WRC', choices=[
        ('WRC', 'WRC'), ('EMA', 'EMA'), ('custom', 'custom')
        ], validators=[DataRequired()])

    url = StringField('Tournament URL', validators=[Optional(), URL(), url_ok])
    url_icon = StringField('Icon URL', validators=[Optional(), URL(), url_ok])
    google_doc_id = StringField('Google Doc ID', validators=[
        DataRequired(),
        validate_google_doc_id])
    web_directory = StringField('Web Directory', validators=[
        DataRequired(),
        validate_web_directory])
    submit = SubmitField('Submit')


def get_tournament_data(firebase_id):
    ref = firestore_client.collection("tournaments").document(firebase_id)
    doc = ref.get()
    if doc.exists:
        return doc.to_dict()
    return None


def update_tournament_data(firebase_id, data):
    ref = firestore_client.collection("tournaments").document(firebase_id)
    ref.update(data)


def get_dates_from_sheet():
    vals:list = googlesheet.get_raw_schedule(
        googlesheet.get_sheet(current_user.live_tournament.google_doc_id))
    timezone = vals[0][2]
    start_date = vals[2][2]
    end_date = vals[-1][2]
    return (timezone, start_date, end_date)

@blueprint.route('/run/edit', methods=['GET', 'POST'])
@login_required
def edit_tournament():
    firebase_id = current_user.live_tournament.firebase_doc
    dates = get_dates_from_sheet()
    form = TournamentForm(dates[1], dates[2])

    if request.method == 'GET':
        tournament_data = get_tournament_data(firebase_id)
        if tournament_data:
            form.process(data=tournament_data)

        # Populate form with local database data
        form.google_doc_id.data = current_user.live_tournament.google_doc_id
        form.web_directory.data = current_user.live_tournament.web_directory.replace('/home/model/', '')
    else:
        if form.validate_on_submit():
            updated_data = {
                'name': form.name.data,
                'address': form.address.data,
                'country': form.country.data,
                'start_date': form.start_date.data,
                'end_date': form.end_date.data,
                'rules': form.rules.data,
                'status': form.status.data,
                'url': form.url.data,
                'url_icon': form.url_icon.data
            }
            firebase_id = current_user.live_tournament.firebase_doc
            update_tournament_data(firebase_id, updated_data)

            # Update local database
            current_user.live_tournament.google_doc_id = form.google_doc_id.data
            current_user.live_tournament.web_directory = os.path.join('/home/model', form.web_directory.data)
            db.session.commit()

            flash('Tournament data updated successfully', 'success')
            return redirect(url_for('run.run_tournament'))

        flash('validation failed', 'error')

    return render_template(
        'cloud_edit.html',
        form=form,
        firebase_id=firebase_id,
        timezone=dates[0],
        span= f"{dates[1]} - {dates[2]}",
        )
