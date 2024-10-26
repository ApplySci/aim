from flask import Blueprint, jsonify, request, render_template, session
from flask_login import current_user

from oauth_setup import admin_or_editor_required, login_required, tournament_required
from .reassign import fill_table_gaps
from write_sheet import googlesheet

# Remove the blueprint creation from here
# blueprint = Blueprint("sub", __name__)


# Remove the '/sub' prefix from all routes
@admin_or_editor_required
@tournament_required
@login_required
def player_substitution():
    return render_template("player_substitution.html")


@admin_or_editor_required
@tournament_required
@login_required
def get_players_data():
    tournament = current_user.live_tournament
    sheet = googlesheet.get_sheet(tournament.google_doc_id)
    players = googlesheet.get_players(sheet)

    current_players = [p for p in players if p["status"] == "active"]
    substitutes = [p for p in players if p["status"] == "substitute"]

    return jsonify(
        {
            "players": players,
            "current_players": current_players,
            "substitutes": substitutes,
        }
    )


@admin_or_editor_required
@tournament_required
@login_required
def calculate_substitutions():
    data = request.json
    dropped_out = data["dropped_out"]
    substitutes = data["substitutes"]

    tournament = current_user.live_tournament
    sheet = googlesheet.get_sheet(tournament.google_doc_id)
    seating = googlesheet.get_seating(sheet)

    new_seating = fill_table_gaps(
        seats=seating,
        fixed_rounds=4,  # Adjust this value as needed
        omit_players=dropped_out,
        substitutes=substitutes,
        time_limit_seconds=30,
        verbose=True,
    )

    preview = generate_substitution_preview(seating, new_seating)

    session["new_seating"] = new_seating

    return jsonify({"preview": preview})


@admin_or_editor_required
@tournament_required
@login_required
def confirm_substitutions():
    new_seating = session.pop("new_seating", None)
    if not new_seating:
        return jsonify({"status": "error", "message": "No substitution data found"})

    tournament = current_user.live_tournament
    sheet = googlesheet.get_sheet(tournament.google_doc_id)

    googlesheet.update_seating(sheet, new_seating)

    session["last_seating"] = googlesheet.get_seating(sheet)

    return jsonify({"status": "success"})


@admin_or_editor_required
@tournament_required
@login_required
def undo_substitution():
    last_seating = session.pop("last_seating", None)
    if not last_seating:
        return jsonify({"status": "error", "message": "No previous seating found"})

    tournament = current_user.live_tournament
    sheet = googlesheet.get_sheet(tournament.google_doc_id)

    googlesheet.update_seating(sheet, last_seating)

    return jsonify({"status": "success"})


@admin_or_editor_required
@login_required
def generate_substitution_preview(old_seating, new_seating):
    preview = []
    for round_num, (old_round, new_round) in enumerate(
        zip(old_seating, new_seating), 1
    ):
        round_changes = []
        for table_num, (old_table, new_table) in enumerate(
            zip(old_round, new_round), 1
        ):
            table_changes = []
            for seat_num, (old_player, new_player) in enumerate(
                zip(old_table, new_table), 1
            ):
                if old_player != new_player:
                    table_changes.append(
                        f"Seat {seat_num}: {old_player} -> {new_player}"
                    )
            if table_changes:
                round_changes.append(f"Table {table_num}: {', '.join(table_changes)}")
        if round_changes:
            preview.append(f"Round {round_num}: {'; '.join(round_changes)}")
    return preview
