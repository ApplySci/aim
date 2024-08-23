# -*- coding: utf-8 -*-
"""
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
        response = requests.get(field.data)
        if response.status_code != 200:
            raise ValidationError('URL must be valid and return a 200 status code.')
    except requests.exceptions.RequestException:
        raise ValidationError('URL must be valid and return a 200 status code.')


def start_date_check(form, field):
    return
    given_datetime = datetime(2024, 6, 14)  # replace with your datetime
    if field.data > given_datetime:
        raise ValidationError('Start date must be earlier than or equal to start of first hanchan:')


def end_date_check(form, field):
    return
    given_datetime = datetime(2024, 6, 20)  # replace with your datetime
    if field.data < given_datetime:
        raise ValidationError('End date must be later than or equal to given datetime.')


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
    start_date = DateTimeLocalField(
        'Start Date', format='%Y-%m-%dT%H:%M',
        validators=[DataRequired(), start_date_check])
    end_date = DateTimeLocalField(
        'End Date', format='%Y-%m-%dT%H:%M',
        validators=[DataRequired(), end_date_check])
    address = StringField('Address', validators=[DataRequired()])
    countries = sorted([(country.alpha_2, country.name) \
                       for country in pycountry.countries],
                       key= lambda e:e[1])
    country = SelectField('Country', choices=countries)
    name = StringField('Name', validators=[DataRequired()])
    status = RadioField('Status', choices=[
        ('testing', 'Testing'), ('pending', 'Pending'), ('live', 'Live'),
        ('finished', 'Finished')
        ], validators=[DataRequired()])
    rules = RadioField('Rules', choices=[
        ('EMA', 'EMA'), ('WRC', 'WRC'), ('custom', 'custom')
    ], validators=[DataRequired()])
    url = StringField('Tournament URL', validators=[Optional(), URL(), url_ok])
    url_icon = StringField('Icon URL', validators=[Optional(), URL(), url_ok])
    google_doc_id = StringField('Google Doc ID', validators=[DataRequired(), validate_google_doc_id])
    web_directory = StringField('Web Directory', validators=[DataRequired(), validate_web_directory])
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



@blueprint.route('/run/edit', methods=['GET'])
@login_required
def create_edit_tournament_form():
    firebase_id = current_user.live_tournament.firebase_doc
    form = TournamentForm()

    if request.method == 'GET':
        tournament_data = get_tournament_data(firebase_id)
        if tournament_data:
            form.process(data=tournament_data)

        # Populate form with local database data
        form.google_doc_id.data = current_user.live_tournament.google_doc_id
        form.web_directory.data = current_user.live_tournament.web_directory.replace('/home/model/', '')

    return render_template('cloud_edit.html', form=form, firebase_id=firebase_id)


@blueprint.route('/run/edit', methods=['POST'])
@login_required
def edit_tournament():
    firebase_id = current_user.live_tournament.firebase_doc
    form = TournamentForm()

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
        print(f'validated ok, saving {updated_data}')
        update_tournament_data(firebase_id, updated_data)

        # Update local database
        current_user.live_tournament.google_doc_id = form.google_doc_id.data
        current_user.live_tournament.web_directory = os.path.join('/home/model', form.web_directory.data)
        db.session.commit()

        flash('Tournament data updated successfully', 'success')
        return redirect(url_for('run.run_tournament'))

    flash('validation failed')
    return render_template('cloud_edit.html', form=form, firebase_id=firebase_id)
