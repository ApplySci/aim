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
from .reassign import fill_table_gaps
from write_sheet import googlesheet

blueprint = Blueprint("sub", __name__, url_prefix="/sub")


@blueprint.route("/player_substitution")
@admin_or_editor_required
@tournament_required
@login_required
def player_substitution():
    tournament = current_user.live_tournament
    sheet = googlesheet.get_sheet(tournament.google_doc_id)
    completed_rounds = googlesheet.get_completed_rounds(sheet)

    # Get players data
    raw_players = googlesheet.get_players(sheet)
    players = []
    for p in raw_players:
        player = {
            "registration_id": str(p[1]),
            "seating_id": p[0] if p[0] != "" else None,
            "name": p[2],
            "is_current": p[0] != "",  # True if the player has a seating_id
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
    )


@blueprint.route("/get_completed_rounds")
@admin_or_editor_required
@tournament_required
@login_required
def get_completed_rounds():
    tournament = current_user.live_tournament
    sheet = googlesheet.get_sheet(tournament.google_doc_id)
    completed_rounds = googlesheet.get_completed_rounds(sheet)
    return jsonify({"completed_rounds": completed_rounds})


@blueprint.route("/calculate_substitutions", methods=["POST"])
@admin_or_editor_required
@tournament_required
@login_required
def calculate_substitutions():
    data = request.json
    # Store the calculation data in session
    session["calculation_data"] = data
    return jsonify({"status": "success"})


@blueprint.route("/stream_progress")
@admin_or_editor_required
@tournament_required
@login_required
def stream_progress():
    data = session.get("calculation_data")
    if not data:
        return Response("No calculation in progress", status=400)

    dropped_out = data["dropped_out"]
    fixed_rounds = data["fixed_rounds"]

    tournament = current_user.live_tournament
    sheet = googlesheet.get_sheet(tournament.google_doc_id)
    seatlist = googlesheet.get_seating(sheet)
    seating = seatlist_to_seating(seatlist)
    first_sub = 1 + max(max(t) for t in seating[0])

    def generate():
        progress_messages = []

        def log_callback(message, end="\n"):
            # Add message to our queue
            progress_messages.append(message + end)
            print(f"Progress message queued: {message}")  # Server-side debug

        try:
            yield f"data: {json.dumps({'log': 'Starting calculation...\n'})}\n\n"
            time.sleep(0.1)  # Small delay to ensure client receives initial message

            new_seating = fill_table_gaps(
                seats=seating,
                fixed_rounds=fixed_rounds,
                omit_players=dropped_out,
                substitutes=range(first_sub, first_sub + 4),
                time_limit_seconds=300,
                verbose=True,
                log_callback=log_callback,
            )

            # Send any queued messages
            for message in progress_messages:
                yield f"data: {json.dumps({'log': message})}\n\n"
                time.sleep(0.05)  # Small delay between messages

            yield f"data: {json.dumps({'log': 'Calculation complete, generating preview...\n'})}\n\n"
            time.sleep(0.1)

            preview = generate_substitution_preview(seating, new_seating)
            session["new_seating"] = new_seating
            yield f"data: {json.dumps({'preview': preview})}\n\n"

        except Exception as e:
            print(f"Error in stream_progress: {str(e)}")
            yield f"data: {json.dumps({'log': f'Error: {str(e)}\n'})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
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

    googlesheet.update_seating(sheet, new_seating)

    session["last_seating"] = googlesheet.get_seating(sheet)

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
