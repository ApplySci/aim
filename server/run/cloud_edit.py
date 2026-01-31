# -*- coding: utf-8 -*-
"""
Tournament metadata editing functionality.

Provides routes and functions for editing tournament information stored in
Firebase cloud storage, including tournament details, schedule, and custom HTML
content. Includes sanitization of user-provided HTML content.
"""
from datetime import datetime, timedelta
import os
import json
from zoneinfo import ZoneInfo

import bleach
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    jsonify,
    abort,
)
from flask_login import current_user, login_required
from functools import wraps
from wtforms import (
    DateTimeLocalField,
    RadioField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Optional, URL, ValidationError

from config import BASEDIR
from forms.tournament_forms import EditTournamentForm
from oauth_setup import db, firestore_client, admin_or_editor_required, logging, Role
from write_sheet import googlesheet

blueprint = Blueprint("edit", __name__)

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


def validate_web_directory(form, field):
    full_path = os.path.join(BASEDIR, field.data)
    if not os.path.isdir(full_path):
        raise ValidationError("Directory does not exist")


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
    vals: list = googlesheet.get_raw_schedule(
        googlesheet.get_sheet(current_user.live_tournament.google_doc_id)
    )
    timezone = vals[0][2]
    start_date = vals[2][2]
    end_date = vals[-1][2]
    return (timezone, start_date, end_date)


@blueprint.route("/run/edit", methods=["GET", "POST"])
@admin_or_editor_required
@login_required
def edit_tournament():
    firebase_id = current_user.live_tournament.firebase_doc
    dates = get_dates_from_sheet()

    # Parse the dates from the sheet (these are hanchan start times in local timezone)
    first_hanchan = datetime.strptime(dates[1], "%A %d %B %Y, %H:%M")
    last_hanchan = datetime.strptime(dates[2], "%A %d %B %Y, %H:%M")
    
    # Calculate suggested tournament start/end times using same offsets as creation
    # Start: 45 minutes before first hanchan
    # End: 150 minutes after last hanchan starts
    suggested_start = first_hanchan - timedelta(minutes=45)
    suggested_end = last_hanchan + timedelta(minutes=150)

    formatted_start_date = suggested_start.strftime("%Y-%m-%dT%H:%M")
    formatted_end_date = suggested_end.strftime("%Y-%m-%dT%H:%M")

    # Format in friendly format for button text
    friendly_start_date = suggested_start.strftime("%A %d %B %Y, %H:%M")
    friendly_end_date = suggested_end.strftime("%A %d %B %Y, %H:%M")

    form = EditTournamentForm(
        is_edit=True, custom_start_date=first_hanchan, custom_end_date=last_hanchan
    )

    if request.method == "GET":
        tournament_data = get_tournament_data(firebase_id)
        if tournament_data:
            # Convert UTC dates from Firestore to local timezone for display
            timezone_string = dates[0]
            tz = ZoneInfo(timezone_string)
            if tournament_data.get("start_date"):
                start_dt = tournament_data["start_date"]
                # If it's a timezone-aware datetime, convert to local time
                if hasattr(start_dt, 'tzinfo') and start_dt.tzinfo is not None:
                    tournament_data["start_date"] = start_dt.astimezone(tz).replace(tzinfo=None)
            if tournament_data.get("end_date"):
                end_dt = tournament_data["end_date"]
                if hasattr(end_dt, 'tzinfo') and end_dt.tzinfo is not None:
                    tournament_data["end_date"] = end_dt.astimezone(tz).replace(tzinfo=None)
            
            form.process(data=tournament_data)

        # Populate form with local database data
        form.google_doc_id.data = current_user.live_tournament.google_doc_id
        form.web_directory.data = current_user.live_tournament.web_directory
        form.title.data = current_user.live_tournament.title
        form.status.data = current_user.live_tournament.status
    else:
        if form.validate_on_submit():
            # Convert naive local datetimes to timezone-aware UTC datetimes
            # (same as how hanchan times are handled in write_sheet.py)
            timezone_string = dates[0]
            tz = ZoneInfo(timezone_string)
            start_date_utc = None
            end_date_utc = None
            if form.start_date.data:
                start_date_utc = form.start_date.data.replace(tzinfo=tz).astimezone(ZoneInfo("UTC"))
            if form.end_date.data:
                end_date_utc = form.end_date.data.replace(tzinfo=tz).astimezone(ZoneInfo("UTC"))

            updated_data = {
                "name": form.title.data,
                "address": form.address.data,
                "country": form.country.data,
                "start_date": start_date_utc,
                "end_date": end_date_utc,
                "rules": form.rules.data,
                "status": form.status.data,
                "url": form.url.data,
                "url_icon": form.url_icon.data,
                "use_winds": form.use_winds.data,
                "htmlnotes": bleach.clean(
                    form.htmlnotes.data,
                    tags=ALLOWED_TAGS,
                    attributes={"a": ["href", "title"]},
                    strip=True,
                ),
            }
            firebase_id = current_user.live_tournament.firebase_doc
            update_tournament_data(firebase_id, updated_data)

            # Update local database
            current_user.live_tournament.title = form.title.data
            current_user.live_tournament.google_doc_id = form.google_doc_id.data
            current_user.live_tournament.web_directory = form.web_directory.data

            # Update status in Firebase
            ref = firestore_client.collection("tournaments").document(firebase_id)
            ref.update({"status": form.status.data})

            # Clear the cached status
            if "status" in current_user.live_tournament.__dict__:
                del current_user.live_tournament.__dict__["status"]

            db.session.commit()

            # Create the web directory if it doesn't exist
            full_path = os.path.join(BASEDIR, form.web_directory.data)
            if not os.path.exists(full_path):
                try:
                    os.makedirs(full_path)
                except OSError:
                    flash("Failed to create web directory", "error")
                    return render_template(
                        "cloud_edit.html",
                        form=form,
                        firebase_id=firebase_id,
                        timezone=dates[0],
                        span=f"{dates[1]} - {dates[2]}",
                    )

            flash("Tournament data updated successfully", "success")
            return redirect(url_for("run.run_tournament"))

        flash("validation failed", "error")
        logging.error("Form validation failed. Specific errors:")
        for field, errors in form.errors.items():
            for error in errors:
                logging.error(f"Field '{field}': {error}")

    return render_template(
        "cloud_edit.html",
        form=form,
        firebase_id=firebase_id,
        timezone=dates[0],
        startdate=formatted_start_date,
        enddate=formatted_end_date,
        friendly_startdate=friendly_start_date,
        friendly_enddate=friendly_end_date,
    )


@blueprint.route("/run/validate_google_doc", methods=["POST"])
@login_required
def validate_google_doc():
    doc_id = request.form.get("doc_id")
    try:
        googlesheet.get_sheet(doc_id)
        return jsonify({"valid": True})
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)})
