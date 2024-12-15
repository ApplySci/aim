from flask import (
    Blueprint,
    jsonify,
    request,
    render_template,
    session,
    Response,
    stream_with_context,
)
from flask_login import current_user
import json
import time

from oauth_setup import (
    admin_or_editor_required,
    logging,
    login_required,
    tournament_required,
)
from write_sheet import googlesheet

blueprint = Blueprint("sub", __name__, url_prefix="/sub")


@blueprint.route("/player_substitution")
@admin_or_editor_required
@tournament_required
@login_required
def player_substitution():
    tournament = current_user.live_tournament
    sheet = googlesheet.get_sheet(tournament.google_doc_id)
    completed_rounds = googlesheet.count_completed_hanchan(sheet)

    # Get players data
    raw_players = googlesheet.get_players(sheet)
    players = []

    # Initialize counters
    players_with_seating = 0
    subs_with_seating = 0
    subs_without_seating = 0

    for p in raw_players:
        has_seating = p[0] != ""
        is_sub = "sub" in str(p[1]).lower()  # Check registration ID for "sub"

        # Update counters
        if has_seating:
            players_with_seating += 1
            if is_sub:
                subs_with_seating += 1
        elif is_sub:
            subs_without_seating += 1

        player = {
            "registration_id": str(p[1]),
            "seating_id": p[0] if has_seating else None,
            "name": p[2],
            "is_current": has_seating,
        }
        players.append(player)

    # Get current seating arrangement
    seatlist = googlesheet.get_seating(sheet)
    seating = seatlist_to_seating(seatlist)

    return render_template(
        "player_substitution.html",
        completed_rounds=completed_rounds,
        players=players,
        seating=seating,
        players_with_seating=players_with_seating,
        subs_with_seating=subs_with_seating,
        subs_without_seating=subs_without_seating,
    )


@blueprint.route("/confirm_substitutions", methods=["POST"])
@admin_or_editor_required
@tournament_required
@login_required
def confirm_substitutions():
    new_seating = session.pop("new_seating", None)
    if not new_seating:
        return jsonify({"status": "error", "message": "No substitution data found"})

    tournament = current_user.live_tournament
    sheet = googlesheet.get_sheet(tournament.google_doc_id)
    seatlist = seating_to_seatlist(new_seating)
    session["last_seating"] = googlesheet.get_seating(sheet)
    googlesheet.update_seating(sheet, seatlist)
    return jsonify({"status": "success"})


@blueprint.route("/undo_substitution", methods=["POST"])
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


def seatlist_to_seating(seatlist):
    hanchan_count = max([p[0] for p in seatlist])
    table_count = max([p[1] for p in seatlist])
    seating = [[[] for _ in range(table_count)] for _ in range(hanchan_count)]
    for p in seatlist:
        seating[p[0] - 1][p[1] - 1] = p[2:]
    return seating


def seating_to_seatlist(seating):
    return [
        (
            h + 1,
            t + 1,
            seating[h][t][0],
            seating[h][t][1],
            seating[h][t][2],
            seating[h][t][3],
        )
        for h in range(len(seating))
        for t in range(len(seating[h]))
    ]


@blueprint.route("/store_seating", methods=["POST"])
@admin_or_editor_required
@tournament_required
@login_required
def store_seating():
    data = request.json
    if not data or "seating" not in data:
        return jsonify({"status": "error", "message": "No seating data provided"}), 400

    session["new_seating"] = data["seating"]
    return jsonify({"status": "success"})


@blueprint.route("/analyze_seating", methods=["POST"])
@admin_or_editor_required
@tournament_required
@login_required
def analyze_seating():
    data = request.json
    if not data or "seating" not in data:
        return jsonify({"status": "error", "message": "No seating data provided"}), 400

    from seating.gams.make_stats import make_stats

    # Get current seating for comparison
    tournament = current_user.live_tournament
    sheet = googlesheet.get_sheet(tournament.google_doc_id)
    current_seatlist = googlesheet.get_seating(sheet)
    current_seating = seatlist_to_seating(current_seatlist)

    # Find the highest player ID in the current seating
    max_id = max(
        max(player for table in round for player in table) for round in current_seating
    )

    # Create list of substitute IDs (will be max_id + 1, max_id + 2, etc.)
    substitute_ids = [0] + list(range(max_id + 1, max_id + 4))

    # Calculate stats for both seating arrangements
    current_stats = make_stats(current_seating, ignore_players=substitute_ids)
    new_stats = make_stats(data["seating"], ignore_players=substitute_ids)

    return jsonify({"status": "success", "current": current_stats, "new": new_stats})
