# -*- coding: utf-8 -*-
"""
Administrative functionality.

Provides routes and functions for tournament administration,
including regenerating past tournament data, managing access permissions,
and other administrative tasks. Restricted to users with admin privileges.
"""

from functools import wraps
import os
import shutil

from flask import abort, Blueprint, flash, jsonify, redirect, render_template, url_for
from flask_login import login_required, current_user

from config import GOOGLE_CLIENT_EMAIL, OUR_EMAILS, SUPERADMIN, TEMPLATE_ID
from models import Tournament, Access, User, PastTournamentData
from oauth_setup import db, firestore_client, login_required, superadmin_required
from operations.archive import update_past_tournaments_json
from operations.queries import get_past_tournament_summaries
from write_sheet import googlesheet


blueprint = Blueprint("admin", __name__)


@blueprint.route("/regenerate_past_tournaments", methods=["POST"])
@login_required
def regenerate_past_tournaments():
    if current_user.email != SUPERADMIN:
        flash("Unauthorized", "error")
        return redirect(url_for("admin.superadmin"))

    try:
        tournaments = get_past_tournament_summaries()
        update_past_tournaments_json(tournaments)
        flash("Past tournaments JSON regenerated successfully", "success")
    except Exception as e:
        flash(f"Error regenerating past tournaments JSON: {str(e)}", "error")

    return redirect(url_for("admin.superadmin"))


@blueprint.route(
    "/admin/delete_sheet/<doc_id>",
    methods=["DELETE"],
)
@superadmin_required
@login_required
def delete_sheet(doc_id):
    if doc_id == TEMPLATE_ID:
        return "Sorry Dave, I can't do that", 403
    googlesheet.delete_sheet(doc_id)
    return "ok", 204


@blueprint.route(
    "/admin/delete_tournament/<int:t_id>",
    methods=["DELETE"],
)
@superadmin_required
@login_required
def delete_tournament(t_id):
    if t_id < 4:
        return "Sorry Dave, I can't do that", 403

    try:
        # Fetch the tournament
        tournament = db.session.query(Tournament).get(t_id)
        if not tournament:
            return "Tournament not found", 404

        # Delete from Firestore
        if tournament.firebase_doc:
            firestore_client.collection("tournaments").document(
                tournament.firebase_doc
            ).delete()

        # Delete web directory
        if tournament.web_directory:
            web_dir_path = tournament.full_web_directory
            if os.path.exists(web_dir_path):
                shutil.rmtree(web_dir_path)

        # Delete from database tables: Access & Tournament
        db.session.query(Access).filter(Access.tournament_id == t_id).delete()
        db.session.delete(tournament)
        db.session.commit()

        return "Tournament deleted successfully", 200
    except Exception as e:
        db.session.rollback()
        return f"Error deleting tournament: {str(e)}", 500


@blueprint.route("/admin/list")
@superadmin_required
@login_required
def superadmin():
    try:
        # Get active tournaments from Firestore
        active_tournaments = []
        for tournament in (
            db.session.query(Tournament).filter(Tournament.past_data == None).all()
        ):
            if tournament.firebase_doc:
                doc_ref = firestore_client.collection("tournaments").document(
                    tournament.firebase_doc
                )
                doc = doc_ref.get()
                if doc.exists:
                    status = doc.to_dict().get("status")
                    if status in ("upcoming", "test"):
                        active_tournaments.append(tournament)

        # Get archived tournaments
        archived_tournaments = (
            db.session.query(Tournament)
            .join(PastTournamentData)
            .order_by(PastTournamentData.archived_at.desc())
            .all()
        )

        docs = googlesheet.list_sheets(GOOGLE_CLIENT_EMAIL)
        our_docs = [doc for doc in docs if doc["ours"] and doc["id"] != TEMPLATE_ID]

        users_without_access = (
            db.session.query(User)
            .outerjoin(Access)
            .filter(Access.user_email == None)
            .all()
        )

        return render_template(
            "adminlist.html",
            docs=our_docs,
            active_tournaments=active_tournaments,
            archived_tournaments=archived_tournaments,
            users_without_access=users_without_access,
        )
    except Exception as e:
        return f"Error listing sheets: {str(e)}", 500
