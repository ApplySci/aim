# -*- coding: utf-8 -*-
"""
creates the front-end pages for the user to set up a new google scoresheet.
"""
from datetime import datetime, timedelta
from itertools import zip_longest  # Add this import at the top of the file
import os
import threading

from firebase_admin import firestore
from flask import (
    Blueprint,
    jsonify,
    redirect,
    request,
    url_for,
    render_template,
    copy_current_request_context,
)
from flask_login import login_required, current_user

from config import GOOGLE_CLIENT_EMAIL, BASEDIR, SUPERADMIN
from forms.tournament_forms import TournamentForm
from models import Access, Tournament, User
from oauth_setup import db, firestore_client, logging, Role
from run.run import update_schedule
from write_sheet import googlesheet
from utils.timezones import get_timezones_for_country
from run.user_management import get_all_users

blueprint = Blueprint("create", __name__)
messages_by_user = {}


def extract_scorer_emails_from_request(form, request):
    """Extract all scorer emails from form data, including dynamically added fields."""
    scorer_emails = []

    # Get the main scorer_emails field
    if form.scorer_emails.data and form.scorer_emails.data.strip():
        scorer_emails.append(form.scorer_emails.data.strip())

    # Get dynamically added scorer email fields
    for key, value in request.form.items():
        if key.startswith("scorer_emails-") and value and value.strip():
            scorer_emails.append(value.strip())

    # Filter out invalid emails and deduplicate
    valid_emails = []
    for email in scorer_emails:
        if email and email != "." and email not in valid_emails:
            valid_emails.append(email)

    return valid_emails


@blueprint.route("/create/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("run.select_tournament"))
    else:
        return render_template("welcome_anon.html")


@blueprint.route("/create/results", methods=["GET", "POST", "PUT"])
@login_required
def results_create():
    owner = current_user.email
    form = TournamentForm()

    if request.method == "POST":
        round_dates = []
        for key, value in request.form.items():
            if key.startswith("round_dates-") and value:
                try:
                    round_dates.append(datetime.strptime(value, "%Y-%m-%dT%H:%M"))
                except ValueError:
                    # Handle invalid date format
                    pass

        form.set_round_dates(round_dates)

        # Update the choices for the timezone field based on the selected country
        selected_country = request.form.get("country")
        timezones = get_timezones_for_country(selected_country)
        form.timezone.choices = [(tz, tz) for tz in timezones]

    if form.validate_on_submit():
        short_name = form.web_directory.data
        tournament: Tournament = Tournament(
            title=form.title.data,
            web_directory=short_name,
            google_doc_id="pending",
            firebase_doc=short_name,
        )
        db.session.add(tournament)
        db.session.commit()
        current_user.live_tournament = tournament

        # Calculate end_date by adding 3 hours to the last round date
        end_date = form.round_dates[-1].data + timedelta(hours=3)

        firestore_data = {
            "name": form.title.data,
            "start_date": form.round_dates[0].data,
            "end_date": end_date,
            "status": "upcoming",
            "rules": form.rules.data,
            "country": form.country.data,
            "address": form.address.data,
            "url": form.url.data,
            "url_icon": form.url_icon.data,
            "htmlnotes": form.htmlnotes.data,
            "use_winds": form.use_winds.data,
        }

        firestore_client.collection("tournaments").document(short_name).set(
            firestore_data
        )

        # Add access for the current user
        db.session.add(
            Access(current_user.email, tournament=tournament, role=Role.admin)
        )

        # Ensure SUPERADMIN is always an admin for every tournament
        if current_user.email.lower() != SUPERADMIN.lower():
            # Ensure the SUPERADMIN user record exists
            superadmin_user = db.session.query(User).filter_by(email=SUPERADMIN).first()
            if not superadmin_user:
                superadmin_user = User(email=SUPERADMIN)
                db.session.add(superadmin_user)

            # Add SUPERADMIN as admin
            db.session.add(Access(SUPERADMIN, tournament=tournament, role=Role.admin))

        db.session.commit()

        # Extract scorer emails once using helper function
        scorer_emails = extract_scorer_emails_from_request(form, request)

        # Process scorer emails for database access
        for email in scorer_emails:
            scorer = db.session.query(User).filter_by(email=email).first()
            if scorer is None:
                scorer = User(email=email)
                db.session.add(scorer)
            db.session.add(Access(email, tournament=tournament, role=Role.scorer))

        db.session.commit()
        base_dir = tournament.full_web_directory
        os.makedirs(base_dir, exist_ok=True)
        os.makedirs(os.path.join(base_dir, "rounds"), exist_ok=True)
        os.makedirs(os.path.join(base_dir, "players"), exist_ok=True)

        hanchan_count = int(form.hanchan_count.data)
        round_name_template = (
            form.other_name.data
            if form.hanchan_name.data == "other"
            else form.hanchan_name.data
        )
        start_times = [
            request.form.get(f"round_dates-{i}") for i in range(0, hanchan_count)
        ]
        chombo = (
            -30
            if form.rules.data == "WRC"
            else -20 if form.rules.data == "EMA" else None
        )

        @copy_current_request_context
        def make_sheet():
            sheet_id: str = googlesheet.create_new_results_googlesheet(
                table_count=int(form.table_count.data),
                hanchan_count=hanchan_count,
                title=form.title.data,
                owner=owner,
                scorers=scorer_emails,
                notify=form.notify.data,
                timezone=form.timezone.data,
                start_times=start_times,
                round_name_template=round_name_template,
                chombo=chombo,
            )

            try:
                # Store the tournament ID before the database operation
                tournament_id = current_user.live_tournament.id
                
                # Re-fetch the tournament to avoid stale object issues
                tournament = db.session.query(Tournament).get(tournament_id)
                if tournament:
                    tournament.google_doc_id = sheet_id
                    db.session.commit()
                    logging.info(f"Updated tournament {tournament_id} with sheet_id {sheet_id}")
                else:
                    logging.error(f"Tournament {tournament_id} not found during sheet update")
                    
                # Update hyperlinks in the Google Sheet with the actual tournament_id
                googlesheet.update_hyperlinks_with_tournament_id(sheet_id, tournament_id)
                
            except Exception as e:
                logging.error(f"Error updating tournament with sheet_id: {str(e)}")
                db.session.rollback()

        thread = threading.Thread(target=make_sheet)
        thread.start()
        return redirect(url_for("create.select_sheet"))

    logging.warning(
        "*** exceptions arose during validation of submitted tournament creation form"
    )
    for field, errors in form.errors.items():
        for error in errors:
            logging.info(f"Field {field}: {error}")
    # Generate labels for the round dates
    round_labels = []
    template = (
        form.other_name.data
        if form.hanchan_name.data == "other"
        else form.hanchan_name.data
    )
    for i in range(len(form.round_dates)):
        round_labels.append(template.replace("?", str(i + 1)))

    # If the form is not valid or it's a GET request, render the template with the form
    if request.method == "GET" or not form.validate_on_submit():
        initial_country = form.country.data or form.country.default
        initial_timezones = get_timezones_for_country(initial_country)
        form.timezone.choices = [(tz, tz) for tz in initial_timezones]

    return render_template(
        "create_results.html",
        form=form,
        round_labels=round_labels,
        zip=zip_longest,
        all_accounts=get_all_users(),
    )


@blueprint.route("/create/poll_new_sheet")
@login_required
def poll_new_sheet():
    if (
        current_user.live_tournament
        and current_user.live_tournament.google_doc_id != "pending"
    ):
        return jsonify(
            {
                "id": current_user.live_tournament.google_doc_id,
                "title": current_user.live_tournament.title,
            }
        )

    return "not ready yet", 204


def get_used_google_doc_ids():
    """Get a set of Google Doc IDs that are already attached to tournaments."""
    used_doc_ids = set()
    
    # Get all tournaments except the current one being created (if it exists)
    current_tournament_id = None
    if current_user.live_tournament:
        current_tournament_id = current_user.live_tournament.id
    
    # Query for google_doc_ids, excluding "pending" and the current tournament
    query = db.session.query(Tournament.google_doc_id).filter(
        Tournament.google_doc_id != "pending",
        Tournament.google_doc_id.isnot(None)
    )
    
    if current_tournament_id:
        query = query.filter(Tournament.id != current_tournament_id)
    
    # Extract the google_doc_ids from the query results
    for (doc_id,) in query:
        used_doc_ids.add(doc_id)
    
    return used_doc_ids


@blueprint.route("/create/copy_made")
@login_required
def get_their_copy():
    # Get all Google Doc IDs that are already used by other tournaments
    used_doc_ids = get_used_google_doc_ids()
    
    # TODO TOFIX this doesn't seem to be working properly
    docs = googlesheet.list_sheets(current_user.email)
    their_docs = []
    for doc in docs:
        # Filter out sheets that are:
        # 1. Ours (system-owned)
        # 2. Already attached to other tournaments
        # 3. Have "score-template" in the title (template sheets)
        if (not doc["ours"] and 
            doc["id"] not in used_doc_ids and 
            "score-template" not in doc["title"].lower()):
            their_docs.append(doc)
    if their_docs:
        return jsonify(their_docs)
    return "none found", 204


@blueprint.route("/create/select/<doc>", methods=["POST", "GET", "PUT"])
@login_required
def google_doc_selected(doc):
    current_user.live_tournament.google_doc_id = doc
    db.session.commit()
    update_schedule()
    return redirect(url_for("run.run_tournament"))


@blueprint.route("/create/select_sheet", methods=["GET", "POST", "PUT"])
@login_required
def select_sheet():
    docs = messages_by_user.get(current_user.email)
    return render_template(
        "sheet_wip.html",
        docs=docs,
        OUR_EMAIL=GOOGLE_CLIENT_EMAIL,
    )


@blueprint.route("/get_timezones/<country>")
@login_required
def get_timezones(country):
    timezones = get_timezones_for_country(country)
    return jsonify(sorted(timezones))
