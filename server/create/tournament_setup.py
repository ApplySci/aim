# -*- coding: utf-8 -*-
"""
creates the front-end pages for the user to set up a new google scoresheet.
"""
from datetime import datetime
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
    current_app,
    copy_current_request_context,
)
from flask_login import login_required, current_user

from config import GOOGLE_CLIENT_EMAIL
from forms.tournament_forms import TournamentForm
from models import Access, Role, Tournament, User
from oauth_setup import db, firestore_client
from write_sheet import googlesheet


blueprint = Blueprint("create", __name__)
messages_by_user = {}


@blueprint.route("/create/")
def index():
    if current_user.is_authenticated:
        return render_template("welcome_admin.html")
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

        firestore_data = {
            "name": form.title.data,
            "start_date": form.round_dates[0].data,
            "end_date": form.round_dates[-1].data,
            "status": "upcoming",
            "rules": form.rules.data,
            "country": form.country.data,
            "address": form.address.data,
            "url": form.url.data,
            "url_icon": form.url_icon.data,
            "htmlnotes": form.htmlnotes.data,
        }

        firestore_client.collection("tournaments").document(short_name).set(firestore_data)

        # Add access for the current user
        db.session.add(
            Access(user=current_user, tournament=tournament, role=Role.admin)
        )
        db.session.commit()
        for email in form.scorer_emails.data:
            if email:  # Only process non-empty email fields
                scorer = db.session.query(User).filter_by(email=email).first()
                if scorer is None:
                    scorer = User(email=email)
                    db.session.add(scorer)
                db.session.add(Access(user=scorer, tournament=tournament, role=Role.scorer))
        db.session.commit()
        base_dir = os.path.join("myapp/static", form.web_directory.data)
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

        @copy_current_request_context
        def make_sheet():
            sheet_id: str = googlesheet.create_new_results_googlesheet(
                table_count=int(form.table_count.data),
                hanchan_count=hanchan_count,
                title=form.title.data,
                owner=owner,
                scorers=form.emails.data.split(",") if form.emails.data else [],
                notify=form.notify.data,
                timezone=form.timezone.data,
                start_times=start_times,
                round_name_template=round_name_template,
            )

            msg = messages_by_user.get(owner)
            if not msg:
                messages_by_user[owner] = []
            messages_by_user[owner].append(
                {
                    "id": sheet_id,
                    "title": form.title.data,
                    "ours": True,
                }
            )

        thread = threading.Thread(target=make_sheet)
        thread.start()
        return redirect(url_for("create.select_sheet"))

    print('*** failed validation')
    for field, errors in form.errors.items():
        for error in errors:
            print(f"Field {field}: {error}")
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
    return render_template(
        "create_results.html", form=form, round_labels=round_labels, zip=zip_longest
    )


@blueprint.route("/create/is_sheet_created")
@login_required
def poll_new_sheet():
    messages = messages_by_user.get(current_user.email)
    if messages:
        for message in messages:
            current_app.logger.warning(f"in poll_new_sheet with {message}")
            if message["ours"]:
                current_app.logger.warning("sending it!")
                return jsonify(message)

    return "not ready yet", 204


@blueprint.route("/create/copy_made")
@login_required
def get_their_copy():
    docs = googlesheet.list_sheets(current_user.email)
    their_docs = []
    for doc in docs:
        if not doc["ours"]:
            their_docs.append(doc)
    if their_docs:
        return jsonify(their_docs)
    return "none found", 204


@blueprint.route("/create/select/<doc>", methods=["POST", "GET", "PUT"])
@login_required
def google_doc_selected(doc):
    # TODO add to the firebase database too!
    # and then add the database document ID to our local db here
    title = request.form.get("submit")
    tournament = _add_to_db(doc, title)
    current_user.live_tournament_id = tournament.id
    db.session.commit()
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


def _add_to_db(doc, title):
    tournament = db.session.query(Tournament).filter_by(google_doc_id=doc).first()
    if not tournament:
        tournament = Tournament(google_doc_id=doc, title=title)
        db.session.add(tournament)

    access = (
        db.session.query(Access)
        .filter_by(
            user_email=current_user.email,
            tournament_id=tournament.id,
        )
        .first()
    )
    if not access:
        access = Access(user=current_user, tournament=tournament, role=Role.admin)
        db.session.add(access)
    db.session.commit()
    return tournament
