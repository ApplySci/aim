# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, jsonify
from flask_login import current_user, login_required
import os
import shutil
from config import GOOGLE_CLIENT_EMAIL, OUR_EMAILS, TEMPLATE_ID
from write_sheet import googlesheet
from models import Tournament, Access
from oauth_setup import db, firestore_client

blueprint = Blueprint("admin", __name__)


@blueprint.route(
    "/admin/delete_sheet/<doc_id>",
    methods=["DELETE"],
)
@login_required
def delete_sheet(doc_id):
    if current_user.email not in OUR_EMAILS:
        return "not found", 404
    if doc_id == TEMPLATE_ID:
        return "Sorry Dave, I can't do that", 403
    googlesheet.delete_sheet(doc_id)
    return "ok", 204


@blueprint.route(
    "/admin/delete_tournament/<int:t_id>",
    methods=["DELETE"],
)
@login_required
def delete_tournament(t_id):
    if current_user.email not in OUR_EMAILS:
        return "not found", 404
    if t_id < 4:
        return "Sorry Dave, I can't do that", 403
    
    try:
        # Fetch the tournament
        tournament = db.session.query(Tournament).get(t_id)
        if not tournament:
            return "Tournament not found", 404

        # Delete from Firestore
        if tournament.firebase_doc:
            firestore_client.collection('tournaments').document(tournament.firebase_doc).delete()

        # Delete web directory
        if tournament.web_directory:
            web_dir_path = f"myapp/static/{tournament.web_directory}"
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
@login_required
def superuser():
    if current_user.email not in OUR_EMAILS:
        return "not found", 404
    try:
        # Fetch all tournaments from the database
        all_tournaments = db.session.query(Tournament).all()
        
        # Filter tournaments based on Firestore status
        filtered_tournaments = []
        for tournament in all_tournaments:
            if tournament.firebase_doc:
                doc_ref = firestore_client.collection('tournaments').document(tournament.firebase_doc)
                doc = doc_ref.get()
                if doc.exists:
                    status = doc.to_dict().get('status')
                    if status in ('upcoming', 'test'):
                        filtered_tournaments.append(tournament)

        docs = googlesheet.list_sheets(GOOGLE_CLIENT_EMAIL)
        our_docs = [doc for doc in docs if doc['ours'] and doc['id'] != TEMPLATE_ID]

        return render_template('adminlist.html', docs=our_docs, tournaments=filtered_tournaments)
    except Exception as e:
        return f"Error listing sheets: {str(e)}", 500
