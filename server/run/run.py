# -*- coding: utf-8 -*-
"""
pages and backend for the user running the tournament
"""
from functools import wraps
import json
import os
import sys
import threading
import traceback
import uuid
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from firebase_admin import messaging
from flask import (
    Blueprint,
    redirect,
    url_for,
    render_template,
    copy_current_request_context,
    request,
    jsonify,
    make_response,
    abort,
    flash,
)
from flask_login import login_required, current_user

from models import Access, User, Tournament, PastTournamentData
from oauth_setup import db, firestore_client, logging, tournament_required
from operations.queries import (
    get_active_tournaments,
    get_past_tournament_summaries,
)
from operations.transforms import tournaments_to_summaries
from write_sheet import googlesheet
from . import substitutes

blueprint = Blueprint("run", __name__, url_prefix="/run")


def _is_ajax_request():
    """Detect if this is an AJAX request that expects JSON response"""
    # Check if X-Requested-With header is set (common with jQuery/AJAX)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return True

    # Check if request accepts JSON (fetch requests typically send this)
    accept_header = request.headers.get("Accept", "")
    if "application/json" in accept_header:
        return True

    # Check if there's a timestamp parameter (our AJAX buttons add this)
    if request.args.get("t"):
        return True

    return False


def wrap_and_catch(myfunc):
    @wraps(myfunc)
    def wrapper(*args, **kwargs):
        try:
            return myfunc(*args, **kwargs)
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback_details = traceback.extract_tb(exc_traceback)
            # Filter traceback: only the ones we wrote
            stack = [frame for frame in traceback_details if "/myapp" in frame.filename]
            if len(stack):
                frame = stack[-1]
                msg = f"ERROR: {str(e)} in {frame.filename}, line {frame.lineno}, in {frame.name}"
            else:
                msg = f"ERROR: {str(e)}"
            return msg, 200

    return wrapper


@blueprint.route("/select_tournament", methods=["GET", "POST"])
@login_required
def select_tournament():
    # Move the import to the top of the function
    from models import Tournament

    new_id = request.form.get("id")
    if new_id:
        try:
            # Validate that the tournament exists and user has permission
            tournament = db.session.query(Tournament).get(int(new_id))
            if not tournament:
                flash("Tournament not found", "error")
                return redirect(url_for("run.select_tournament"))

            # Check permission using our centralized function
            _check_tournament_permission(tournament)

            # If we get here, permission is granted
            current_user.live_tournament_id = new_id
            db.session.commit()
            flash(f"Switched to tournament: {tournament.title}", "info")
            return redirect(url_for("run.run_tournament"))

        except Exception as e:
            # Handle permission errors gracefully
            if hasattr(e, "code") and e.code == 403:
                flash("You don't have permission to access this tournament", "error")
            else:
                flash("Error selecting tournament", "error")
            return redirect(url_for("run.select_tournament"))

    # Clean up Access database - delete entries without valid tournament or user
    invalid_accesses = (
        db.session.query(Access)
        .filter(
            (Access.tournament_id.notin_(db.session.query(Tournament.id)))
            | (Access.user_email.notin_(db.session.query(User.email)))
        )
        .all()
    )
    for invalid_access in invalid_accesses:
        db.session.delete(invalid_access)

    grouped_tournaments = get_active_tournaments(current_user.email)
    db.session.commit()

    return render_template(
        "select_tournament.html", grouped_tournaments=grouped_tournaments
    )


@login_required
def _ranking_to_web(scores, games, players, done, schedule, tournament=None):
    if tournament is None:
        tournament = current_user.live_tournament
    items = list(scores.items())
    sorted_scores = sorted(items, key=lambda item: item[1]["r"])  # sort by rank
    title = tournament.title
    if done > 0:
        roundName = f"Scores after {schedule['rounds'][done-1]['name']}"
    else:
        roundName = "End-of-round scores will appear here"
    try:
        nextName = schedule["rounds"][done]["name"]
    except:
        nextName = ""
    html = render_template(
        "projector.html",
        title=title,
        scores=sorted_scores,
        round_name=roundName,
        next_roundname=nextName,
        players=players,
        webroot=webroot(tournament),
    )
    fn = os.path.join(tournament.full_web_directory, "projector.html")
    with open(fn, "w", encoding="utf-8") as f:
        f.write(html)

    # ======================================

    scores_by_player = {}
    for r in range(1, done + 1):
        rs = str(r)
        for t in games[rs]:
            for idx, line in games[rs][t].items():
                # Skip entries where player_id is None or empty
                if line[0] is None or line[0] == "":
                    continue
                p = int(line[0])  # Ensure integer key for consistency
                if p not in scores_by_player:
                    scores_by_player[p] = {}
                if line[4] is None:  # Only include players who actually have scores
                    # Skip missing/substitute players entirely rather than including them with None scores
                    logging.info(
                        f"Skipping player {p} in round {r} - no score available (table: {t})"
                    )
                else:
                    scores_by_player[p][r] = (line[4], t)

    # Validate the structure
    for pid_key, rounds_data in scores_by_player.items():
        if not isinstance(pid_key, int):
            logging.error(
                f"DEBUG: Non-integer player ID key: {pid_key} (type: {type(pid_key)})"
            )
        for round_key, round_data in rounds_data.items():
            if not isinstance(round_data, tuple) or len(round_data) != 2:
                logging.error(
                    f"DEBUG: Invalid round data for player {pid_key}, round {round_key}: {round_data} (type: {type(round_data)})"
                )
        if done == 0:
            render_template("noranking.html", title=title, done=done)
        else:
            html = render_template(
                "ranking.html",
                title=title,
                scores=sorted_scores,
                round_name=roundName,
                players=players,
                webroot=webroot(tournament),
                roundNames=_round_names(schedule),
                done=done,
                games=scores_by_player,
            )
        fn = os.path.join(tournament.full_web_directory, "ranking.html")
        with open(fn, "w", encoding="utf-8") as f:
            f.write(html)


@login_required
def _send_topic_fcm(
    topic: str,
    title: str,
    body: str,
    notification_type: str,
    schedule_data: dict = None,
):
    data = {
        "tournament_id": current_user.live_tournament.firebase_doc,
        "tournament_name": current_user.live_tournament.title,
        "notification_type": notification_type,
    }

    # Include schedule data if provided
    if schedule_data:
        data["schedule_data"] = json.dumps(schedule_data)

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data=data,
        topic=topic,
    )

    try:
        response = messaging.send(message)
    except Exception as e:
        logging.error(f"FCM send failed: {str(e)}", exc_info=True)
        raise


@blueprint.route("/")
@tournament_required
@login_required
def run_tournament():
    tournament = current_user.live_tournament
    sheet = _get_sheet()
    batch_data = googlesheet.batch_get_tournament_data(sheet)
    schedule = googlesheet.get_schedule_from_batch(batch_data)
    hanchan_count = googlesheet.count_completed_hanchan_from_batch(batch_data)

    tournament_tz = ZoneInfo(schedule["timezone"])
    now = datetime.now(tournament_tz)
    first_hanchan = datetime.fromisoformat(schedule["rounds"][0]["start"]).astimezone(
        tournament_tz
    )
    last_hanchan = datetime.fromisoformat(schedule["rounds"][-1]["start"]).astimezone(
        tournament_tz
    )

    expected_status = "live"
    if now < first_hanchan - timedelta(hours=24):
        expected_status = "upcoming"
    elif now > last_hanchan + timedelta(hours=24):
        expected_status = "past"

    current_status = tournament.status
    status_mismatch = current_status != expected_status and current_status != "test"

    return render_template(
        "run_tournament.html",
        webroot=webroot(),
        current_status=current_status,
        expected_status=expected_status,
        status_mismatch=status_mismatch,
        first_hanchan=first_hanchan,
        last_hanchan=last_hanchan,
        now=now,
        tournament_timezone=schedule["timezone"],
        hanchan_count=hanchan_count,
        is_past=(current_status == "past"),
        schedule=schedule,
    )


@blueprint.route("/update_status", methods=["POST"])
@login_required
def update_tournament_status():
    new_status = request.form.get("new_status")
    if new_status in ["live", "past", "test", "upcoming"]:
        tournament = current_user.live_tournament
        tournament_ref = firestore_client.collection("tournaments").document(
            tournament.firebase_doc
        )
        tournament_ref.update({"status": new_status})
        return jsonify({"status": "success", "new_status": new_status})
    return jsonify({"status": "error", "message": "Invalid status"}), 400


@login_required
def _check_tournament_permission(tournament):
    """Check if current user has permission to access the given tournament"""
    from models import Access

    access = (
        db.session.query(Access)
        .filter_by(user_email=current_user.email, tournament_id=tournament.id)
        .first()
    )
    if not access:
        abort(403, description="You don't have permission to access this tournament")
    return tournament


@login_required
def _get_tournament_from_id(tournament_id):
    """Helper function to get tournament object from ID with permission checking"""
    if tournament_id is not None:
        # Get specific tournament and check permission
        from models import Tournament

        tournament = db.session.query(Tournament).get(tournament_id)
        if not tournament:
            abort(404, description="Tournament not found")

        return _check_tournament_permission(tournament)
    else:
        # Use live tournament for legacy URL, but still check permission
        tournament = current_user.live_tournament
        if not tournament:
            abort(404, description="No live tournament set")

        return _check_tournament_permission(tournament)


@login_required
def _get_sheet(tournament=None):
    if tournament is None:
        tournament = current_user.live_tournament
    sheet_id = tournament.google_doc_id
    return googlesheet.get_sheet(sheet_id)


@blueprint.route("/update_schedule")
@blueprint.route("/tournament/<int:tournament_id>/update_schedule")
@login_required
def update_schedule(tournament_id=None):
    try:
        tournament = _get_tournament_from_id(tournament_id)

        sheet = _get_sheet(tournament)
        batch_data = googlesheet.batch_get_tournament_data(sheet)

        schedule = googlesheet.get_schedule_from_batch(batch_data)
        seating = _seating_to_map_from_batch(batch_data, schedule)

        _save_to_cloud(
            "seating",
            {
                "rounds": seating,
                "timezone": schedule["timezone"],
            },
            tournament=tournament,
        )
        _seating_to_web_from_batch(
            batch_data=batch_data, seating=seating, tournament=tournament
        )

        send_notifications = request.args.get("sendNotifications", "true") == "true"

        # Determine the response message
        if send_notifications:
            # Include schedule data in the notification
            notification_schedule_data = {
                "rounds": seating,
                "timezone": schedule["timezone"],
            }
            _send_messages(
                "seating & schedule updated",
                "seating",
                tournament=tournament,
                schedule_data=notification_schedule_data,
            )
            message = "SEATING & SCHEDULE updated, notifications sent"
        else:
            message = "SEATING & SCHEDULE updated, NO notifications"

        # Return JSON for AJAX requests, redirect for regular web requests
        if _is_ajax_request():
            return jsonify({"status": message}), 200
        else:
            return _handle_web_response(message, tournament, "success")
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback_details = traceback.extract_tb(exc_traceback)
        # Filter traceback: only the ones we wrote
        stack = [frame for frame in traceback_details if "/myapp" in frame.filename]
        if len(stack):
            frame = stack[-1]
            error_msg = f"ERROR: {str(e)} in {frame.filename}, line {frame.lineno}, in {frame.name}"
        else:
            error_msg = f"ERROR: {str(e)}"

        # Return JSON for AJAX requests, redirect for regular web requests
        if _is_ajax_request():
            return jsonify({"status": error_msg}), 200
        else:
            return _handle_web_response(error_msg, tournament, "error")


@login_required
def _seating_to_web_from_batch(batch_data, seating, tournament=None):
    if tournament is None:
        tournament = current_user.live_tournament

    done = googlesheet.count_completed_hanchan_from_batch(batch_data)
    players = _get_players_from_batch(batch_data, False, tournament)
    schedule = googlesheet.get_schedule_from_batch(batch_data)

    # Get tournament data from Firestore
    tournament_ref = firestore_client.collection("tournaments").document(
        tournament.firebase_doc
    )
    tournament_data = tournament_ref.get().to_dict()

    html = render_template(
        "seating.html",
        done=done,
        title=tournament.title,
        seating=seating,
        schedule=schedule,
        players=players,
        roundNames=_round_names(schedule),
        use_winds=tournament_data.get("use_winds", False),
    )
    fn = os.path.join(tournament.full_web_directory, "seating.html")
    with open(fn, "w", encoding="utf-8") as f:
        f.write(html)
    return "Seating published on web", 200


@blueprint.route("/update_players")
@blueprint.route("/tournament/<int:tournament_id>/update_players")
@login_required
def update_players(tournament_id=None):
    try:
        tournament = _get_tournament_from_id(tournament_id)

        sheet = _get_sheet(tournament)
        batch_data = googlesheet.batch_get_tournament_data(sheet)
        _get_players_from_batch(batch_data, True, tournament)

        send_notifications = request.args.get("sendNotifications", "true") == "true"

        # Determine the response message
        if send_notifications:
            _send_messages("player list updated", "players", tournament=tournament)
            message = "PLAYERS updated, notifications sent"
        else:
            message = "PLAYERS updated, NO notifications"

        # Return JSON for AJAX requests, redirect for regular web requests
        if _is_ajax_request():
            return jsonify({"status": message}), 200
        else:
            return _handle_web_response(message, tournament, "success")
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback_details = traceback.extract_tb(exc_traceback)
        # Filter traceback: only the ones we wrote
        stack = [frame for frame in traceback_details if "/myapp" in frame.filename]
        if len(stack):
            frame = stack[-1]
            error_msg = f"ERROR: {str(e)} in {frame.filename}, line {frame.lineno}, in {frame.name}"
        else:
            error_msg = f"ERROR: {str(e)}"

        # Return JSON for AJAX requests, redirect for regular web requests
        if _is_ajax_request():
            return jsonify({"status": error_msg}), 200
        else:
            return _handle_web_response(error_msg, tournament, "error")


@login_required
def _send_messages(
    msg: str, notification_type: str, tournament=None, schedule_data: dict = None
):
    if tournament is None:
        tournament = current_user.live_tournament
    firebase_id = tournament.firebase_doc
    _send_topic_fcm(
        firebase_id, msg, tournament.title, notification_type, schedule_data
    )


@login_required
def _message_player_topics(
    scores: dict, done: int, players, tournament=None, batch_data=None
):
    """
    send all our player-specific firebase notifications out
    do this in a separate thread so as not to hold up the main response
    """
    if done == 0:
        return

    if tournament is None:
        tournament = current_user.live_tournament
    firebase_id = tournament.firebase_doc

    # Send general tournament update notification
    topic = f"{firebase_id}-"
    title = f"Scores updated after round {done}"
    body = f"Tournament scores have been updated"
    try:
        _send_topic_fcm(topic, title, body, "scores")
    except Exception as e:
        logging.error(
            f"Failed to send tournament notification: {str(e)}", exc_info=True
        )

    # Get the player map with registration IDs - reuse batch_data if provided
    if batch_data is None:
        batch_data = googlesheet.batch_get_tournament_data(_get_sheet(tournament))
    raw_players = googlesheet.get_players_from_batch(batch_data)
    reg_id_map = {
        p[0]: p[1] for p in raw_players if p[0] != ""
    }  # map seating_id to registration_id

    for k, v in scores.items():
        key = int(k)
        name = players[key] if key < len(players) else f"Player {k}"
        reg_id = reg_id_map.get(key)
        if reg_id:
            topic = f"{firebase_id}-{reg_id}"
            title = f"{name} is now in position {('','=')[v['t']]}{v['r']}"
            body = f"with {v['total']/10} points after {done} round(s)"

            try:
                _send_topic_fcm(topic, title, body, "scores")
            except Exception as e:
                logging.error(
                    f"Failed to send notification to {name}: {str(e)}", exc_info=True
                )


def webroot(tournament=None):
    if tournament is None:
        tournament = current_user.live_tournament
    return f"/static/{tournament.web_directory}/"


def _round_names(schedule):
    roundNames = {}
    for r in schedule["rounds"]:
        roundNames[str(r["id"])] = r["name"]
    return roundNames


@login_required
def _games_to_web(games, schedule, players, tournament=None):
    if tournament is None:
        tournament = current_user.live_tournament
    roundNames = _round_names(schedule)
    player_dir = os.path.join(
        tournament.full_web_directory,
        "players",
    )

    if not os.path.exists(player_dir):
        os.makedirs(player_dir)

    for pid, name in players.items():
        # for each player, create a page with all their games
        try:
            player_games = {}
            for r in games:
                for t in games[r]:
                    present = False
                    for p, s in games[r][t].items():
                        if s[0] == pid:
                            present = True
                            break
                    if present:
                        player_games[r] = {t: games[r][t]}

            html = render_template(
                "player_page.html",
                games=player_games,
                players=players,
                roundNames=roundNames,
                done=len(games),
                webroot=webroot(tournament),
                pid=pid,
                title=tournament.title,
            )

            fn = os.path.join(player_dir, f"{pid}.html")
            with open(fn, "w", encoding="utf-8") as f:
                f.write(html)
        except Exception as e:
            logging.error(
                f"Error writing player page for {pid} ({name}): {e}", exc_info=True
            )

    # =======================================================

    round_dir = os.path.join(
        tournament.full_web_directory,
        "rounds",
    )

    if not os.path.exists(round_dir):
        os.makedirs(round_dir)

    for r in games:
        # for each round, create a page for all its games
        html = render_template(
            "round_page.html",
            games=games[r],
            players=players,
            roundNames=roundNames,
            done=len(games),
            roundname=roundNames[r],
            webroot=webroot(tournament),
            title=tournament.title,
        )

        fn = os.path.join(round_dir, f"{r}.html")
        with open(fn, "w", encoding="utf-8") as f:
            f.write(html)

    return f"{games}", 200


@login_required
def _process_scores_update(tournament, send_notifications=True):
    """
    Core logic for updating scores that can be used by both AJAX and sync requests.
    Returns success message on success, raises exception on error.
    """
    sheet = _get_sheet(tournament)
    # Get preliminary count to know how many rounds to fetch
    done_prelim = googlesheet.count_completed_hanchan(sheet)

    # Use batch get to fetch all data at once
    batch_data = googlesheet.batch_get_tournament_data(
        sheet, include_rounds=done_prelim
    )

    schedule = googlesheet.get_schedule_from_batch(batch_data)
    done = googlesheet.count_completed_hanchan_from_batch(batch_data)
    ranking = _ranking_to_cloud_from_batch(batch_data, done, tournament)
    players = _get_players_from_batch(batch_data, False, tournament)
    games = _games_to_cloud_from_batch(batch_data, done, players, tournament)

    _games_to_web(games, schedule, players, tournament)
    _ranking_to_web(ranking, games, players, done, schedule, tournament)

    if send_notifications:
        _message_player_topics(ranking, done, players, tournament, batch_data)

    return "Scores updated successfully"


@blueprint.route("/update_scores")
@blueprint.route("/tournament/<int:tournament_id>/update_scores")
@login_required
def update_scores(tournament_id=None):
    tournament = _get_tournament_from_id(tournament_id)
    send_notifications = request.args.get("sendNotifications", "true") == "true"
    is_ajax = _is_ajax_request()

    if is_ajax:
        # For AJAX requests, use the background job approach
        job_id = str(uuid.uuid4())

        @copy_current_request_context
        def _finish_sheet_to_cloud():
            try:
                success_msg = _process_scores_update(tournament, send_notifications)
                _store_job_status(job_id, success_msg)
            except Exception as e:
                error_msg = f"Error updating scores: {str(e)}"
                logging.error(error_msg, exc_info=True)
                _store_job_status(job_id, error_msg)

        thread = threading.Thread(target=_finish_sheet_to_cloud)
        thread.start()

        return jsonify({"status": "processing", "job_id": job_id}), 202
    else:
        # For regular web requests, do the work synchronously and redirect
        try:
            success_msg = _process_scores_update(tournament, send_notifications)
            return _handle_web_response(success_msg, tournament, "success")
        except Exception as e:
            error_msg = f"Error updating scores: {str(e)}"
            logging.error(error_msg, exc_info=True)
            return _handle_web_response(error_msg, tournament, "error")


@blueprint.route("/job_status/<job_id>")
@login_required
def get_job_status(job_id):
    status = _get_job_status(job_id)
    response = make_response(jsonify({"status": status}))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


def _store_job_status(job_id, status):
    # You can use a database or cache here. For simplicity, we'll use a global dictionary
    global job_statuses
    job_statuses[job_id] = status


def _get_job_status(job_id):
    global job_statuses
    return job_statuses.get(job_id, "processing")


# Initialize the global dictionary at the top of the file
job_statuses = {}


@login_required
def _games_to_cloud_from_batch(batch_data, done: int, players, tournament=None):
    results = {}
    for this_round in range(1, done + 1):
        tables = googlesheet.get_round_results_from_batch(batch_data, this_round)
        results[str(this_round)] = tables

    cleaned_scores = results.copy()
    for r in cleaned_scores:
        # Track which players played in this round
        has_score = set()
        for t in cleaned_scores[r]:
            for s in cleaned_scores[r][t]:
                has_score.add(cleaned_scores[r][t][s][0])

        # Add null scores for players who didn't play
        # (instead of fake scores with zeros)
        missing = {}
        missed = 0
        for p in players:
            if not p in has_score:
                missing[str(missed)] = [p, None, None, None, None]
                missed += 1
        if missing:
            cleaned_scores[r]["missing"] = missing

    _save_to_cloud("scores", cleaned_scores, force_set=True, tournament=tournament)
    return results


@login_required
def _ranking_to_cloud_from_batch(batch_data, done: int, tournament=None) -> dict:
    results = googlesheet.get_results_from_batch(batch_data)
    body = results[1:]
    body.sort(key=lambda x: -x[3])  # sort by descending cumulative score
    all_scores = {}
    previous_score = -99999
    for i in range(len(body)):
        total = round(10 * body[i][3])
        if previous_score == total:
            tied = 1
        else:
            previous_score = total
            rank = i + 1
            tied = 0

        all_scores[str(body[i][0])] = {
            "total": total,
            "p": round(body[i][4] * 10),
            "r": rank,
            "t": tied,
        }

    round_index: str = f"{done}"
    _save_to_cloud(
        "ranking",
        {round_index: all_scores, "roundDone": round_index},
        tournament=tournament,
    )
    return all_scores


@login_required
def _get_players_from_batch(batch_data, to_cloud=True, tournament=None):
    raw = googlesheet.get_players_from_batch(batch_data)
    players = []
    player_map = {}
    if len(raw) and len(raw[0]) > 2:
        # Find the highest seating_id
        max_seating_id = max((int(p[0]) for p in raw if p[0] != ""), default=0)

        for p in raw:
            registration_id = p[1]
            seating_id = p[0] if p[0] != "" else None
            name = p[2] if len(p) > 2 else f"player {p[1]}"
            is_substitute = seating_id and int(seating_id) > max_seating_id - 3

            player_map[seating_id] = name
            players.append(
                {
                    "registration_id": str(registration_id),
                    "seating_id": seating_id,
                    "name": name,
                    "is_substitute": is_substitute,
                    "is_current": p[0] != "",  # True if the player has a seating_id
                }
            )
    if to_cloud:
        _save_to_cloud("players", {"players": players}, tournament=tournament)
    return player_map


@login_required
def _seating_to_map_from_batch(batch_data, schedule):
    raw = googlesheet.get_seating_from_batch(batch_data)
    seating = []
    previous_round = ""
    hanchan_number = 0
    for t in raw:
        this_round = str(t[0])
        table = str(t[1])
        players = t[2:6]
        if this_round != previous_round:
            previous_round = this_round
            seating.append(
                {
                    "id": this_round,
                    "name": schedule["rounds"][hanchan_number]["name"],
                    "start": schedule["rounds"][hanchan_number]["start"],
                    "tables": {},
                }
            )
            hanchan_number = hanchan_number + 1
        seating[-1]["tables"][table] = [
            f"Player {p}" if p == "" else p for p in players
        ]

    return seating


def _save_to_archive(document: str, data: dict, force_set=False, tournament=None):
    # For past tournaments, save to local database
    if tournament is None:
        tournament = current_user.live_tournament
    if not tournament.past_data:
        return False

    try:
        stored_data = json.loads(tournament.past_data.data)
        if document not in stored_data:
            stored_data[document] = {}
        if force_set:
            stored_data[document] = data
        else:
            stored_data[document].update(data)
        tournament.past_data.data = json.dumps(stored_data)
        db.session.commit()
        return True
    except Exception as e:
        logging.error(f"Error saving past tournament data: {e}")
        db.session.rollback()
        return False


@login_required
def _save_to_cloud(document: str, data: dict, force_set=False, tournament=None):
    if tournament is None:
        tournament = current_user.live_tournament

    if tournament.status == "past":
        return _save_to_archive(document, data, force_set, tournament)

    # For live tournaments, continue using Firebase
    firebase_id: str = tournament.firebase_doc
    for version in ("v3", "v2"):
        ref = firestore_client.collection("tournaments").document(
            f"{firebase_id}/{version}/{document}"
        )
        if version == "v2" and document == "players":
            for p in data["players"]:
                p["id"] = p["seating_id"] or int(p["registration_id"])
        doc = ref.get()
        if doc.exists and not force_set:
            ref.update(data)
        else:
            ref.set(data)
    return True


@blueprint.route("/archive_tournament", methods=["POST"])
@login_required
def archive_tournament():
    """Archive a tournament's data and update its status"""
    tournament = current_user.live_tournament
    if tournament.status != "past":
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Can only archive tournaments with 'past' status",
                }
            ),
            400,
        )

    # Import here to avoid circular imports
    from operations.archive import archive_tournament

    result = archive_tournament(tournament)
    if isinstance(result, dict):
        return jsonify(
            {
                "status": "success",
                "message": "Tournament archived successfully",
                "details": result,
            }
        )

    return jsonify({"status": "error", "message": "Failed to archive tournament"}), 500


# Register the substitutes blueprint
blueprint.register_blueprint(substitutes.blueprint)


@blueprint.route("/past_tournaments")
@login_required
def past_tournaments():
    return render_template("past_tournaments.html")


def _handle_web_response(message, tournament, category="success"):
    """Handle web response with flash message and redirect, ensuring correct live tournament"""
    # Check if the updated tournament is the current user's live tournament
    if current_user.live_tournament_id != tournament.id:
        # Switch to this tournament and notify the user
        current_user.live_tournament_id = tournament.id
        db.session.commit()
        flash(f"Switched to tournament: {tournament.title}", "info")

    # Flash the main action message
    flash(message, category)
    return redirect(url_for("run.run_tournament"))
