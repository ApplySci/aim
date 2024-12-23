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
    new_id = request.form.get("id")
    if new_id:
        current_user.live_tournament_id = new_id
        db.session.commit()
        return redirect(url_for("run.run_tournament"))

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
        "select_tournament.html", 
        grouped_tournaments=grouped_tournaments
    )


@login_required
def _ranking_to_web(scores, games, players, done, schedule):
    items = list(scores.items())
    sorted_scores = sorted(items, key=lambda item: item[1]["r"])  # sort by rank
    title = current_user.live_tournament.title
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
        webroot=webroot(),
    )
    fn = os.path.join(current_user.live_tournament.full_web_directory, "projector.html")
    with open(fn, "w", encoding="utf-8") as f:
        f.write(html)

    # ======================================

    scores_by_player = {}
    for r in range(1, done + 1):
        rs = str(r)
        for t in games[rs]:
            for idx, line in games[rs][t].items():
                p = line[0]
                if p not in scores_by_player:
                    scores_by_player[p] = {}
                scores_by_player[p][r] = (line[4], t)
    if done == 0:
        render_template("noranking.html", title=title, done=done)
    else:
        html = render_template(
            "ranking.html",
            title=title,
            scores=sorted_scores,
            round_name=roundName,
            players=players,
            webroot=webroot(),
            roundNames=_round_names(schedule),
            done=done,
            games=scores_by_player,
        )
    fn = os.path.join(current_user.live_tournament.full_web_directory, "ranking.html")
    with open(fn, "w", encoding="utf-8") as f:
        f.write(html)


@login_required
def _send_topic_fcm(topic: str, title: str, body: str, notification_type: str):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data={
            'tournament_id': current_user.live_tournament.firebase_doc,
            'tournament_name': current_user.live_tournament.title,
            'notification_type': notification_type,
        },
        topic=topic,
    )
    
    logging.info(f"Constructed FCM message: {message}")
    try:
        response = messaging.send(message)
        logging.info(f"FCM send response: {response}")
    except Exception as e:
        logging.error(f"FCM send failed: {str(e)}", exc_info=True)
        raise


@blueprint.route("/")
@tournament_required
@login_required
def run_tournament():
    # TODO add a timer and a way to catch it, to tell the manager to change the schedule,
    # and offer a button to do it quickly, if an alarm is due soon, but the previous
    # hanchan hasn't been published yet
    tournament = current_user.live_tournament
    sheet = _get_sheet()
    schedule = googlesheet.get_schedule(sheet)
    hanchan_count = googlesheet.count_completed_hanchan(sheet)

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
    status_mismatch = current_status != expected_status  # and current_status != 'test'

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
def _get_sheet():
    sheet_id = current_user.live_tournament.google_doc_id
    return googlesheet.get_sheet(sheet_id)


@blueprint.route("/update_schedule")
@wrap_and_catch
@login_required
def update_schedule():
    sheet = _get_sheet()
    schedule: dict = googlesheet.get_schedule(sheet)
    seating = _seating_to_map(sheet, schedule)
    _save_to_cloud(
        "seating",
        {
            "rounds": seating,
            "timezone": schedule["timezone"],
        },
    )
    _seating_to_web(sheet=sheet, seating=seating)

    send_notifications = request.args.get("sendNotifications", "true") == "true"
    if send_notifications:
        _send_messages("seating & schedule updated", 'seating')
        return jsonify({"status": "SEATING & SCHEDULE updated, notifications sent"}), 200
    else:
        return (
            jsonify({"status": "SEATING & SCHEDULE updated, NO notifications"}),
            200,
        )


@login_required
def _seating_to_web(sheet, seating):
    done: int = googlesheet.count_completed_hanchan(sheet)
    players = _get_players(sheet, False)
    schedule: dict = googlesheet.get_schedule(sheet)

    html: str = render_template(
        "seating.html",
        done=done,
        title=current_user.live_tournament.title,
        seating=seating,
        schedule=schedule,
        players=players,
        roundNames=_round_names(schedule),
    )
    fn = os.path.join(current_user.live_tournament.full_web_directory, "seating.html")
    with open(fn, "w", encoding="utf-8") as f:
        f.write(html)
    return "Seating published on web", 200


@blueprint.route("/update_players")
@wrap_and_catch
@login_required
def update_players():
    sheet = _get_sheet()
    _get_players(sheet, True)

    send_notifications = request.args.get("sendNotifications", "true") == "true"
    if send_notifications:
        _send_messages("player list updated", 'players')
        return jsonify({"status": "PLAYERS updated, notifications sent"}), 200
    else:
        return jsonify({"status": "PLAYERS updated, NO notifications"}), 200


@login_required
def _send_messages(msg: str, notification_type: str):
    firebase_id = current_user.live_tournament.firebase_doc
    logging.info(f"Sending tournament-wide notification to topic {firebase_id} with type {notification_type}")
    _send_topic_fcm(firebase_id, msg, current_user.live_tournament.title, notification_type)


@login_required
def _message_player_topics(scores: dict, done: int, players):
    """
    send all our player-specific firebase notifications out
    do this in a separate thread so as not to hold up the main response
    """
    if done == 0:
        return
    
    logging.info(f"Starting player notifications for tournament {current_user.live_tournament.firebase_doc}")
    firebase_id = current_user.live_tournament.firebase_doc
    
    # Send general tournament update notification
    topic = f"{firebase_id}-"
    title = f"Scores updated after round {done}"
    body = f"Tournament scores have been updated"
    try:
        _send_topic_fcm(topic, title, body, 'scores')
        logging.info(f"Sent general tournament update notification")
    except Exception as e:
        logging.error(f"Failed to send tournament notification: {str(e)}", exc_info=True)
    
    # Get the player map with registration IDs
    raw_players = googlesheet.get_players(_get_sheet())
    reg_id_map = {p[0]: p[1] for p in raw_players if p[0] != ""}  # map seating_id to registration_id
    
    for k, v in scores.items():
        name = players[int(k)]
        reg_id = reg_id_map.get(int(k))
        if reg_id:
            topic = f"{firebase_id}-{reg_id}"
            title = f"{name} is now in position {('','=')[v['t']]}{v['r']}"
            body = f"with {v['total']/10} points after {done} round(s)"
            
            try:
                _send_topic_fcm(topic, title, body, 'scores')
                logging.info(f"Successfully sent notification to {name}")
            except Exception as e:
                logging.error(f"Failed to send notification to {name}: {str(e)}", exc_info=True)


@login_required
def _get_one_round_results(sheet, rnd: int):
    vals = googlesheet.get_table_results(round=rnd, live=sheet)
    row: int = 4
    tables = {}
    while row + 3 < len(vals):
        # Get the table number from column 1
        table = f"{vals[row][0]}"
        tables[table] = {}
        if not table:
            # end of score page
            break
        # For each table, get the player ID & scores
        for i in range(4):
            player_id = vals[row + i][1]
            # Handle potential None values in score calculations
            chombo = vals[row + i][5]
            game_score = vals[row + i][3]
            placement = vals[row + i][4]
            final_score = vals[row + i][6]

            tables[table][f"{i}"] = [
                player_id,  # player_id: int
                round(10 * (chombo or 0)),  # chombo: int
                round(10 * (game_score or 0)),  # game score: int
                placement or 0,  # placement: int
                round(10 * (final_score or 0)),  # final score: int
            ]

        # Move to the next table
        row += 7
    return {f"{rnd}": tables}


def webroot():
    return f"/static/{current_user.live_tournament.web_directory}/"


def _round_names(schedule):
    roundNames = {}
    for r in schedule["rounds"]:
        roundNames[r["id"]] = r["name"]
    return roundNames


@login_required
def _games_to_web(games, schedule, players):
    roundNames = _round_names(schedule)
    player_dir = os.path.join(
        current_user.live_tournament.full_web_directory,
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
                webroot=webroot(),
                pid=pid,
                title=current_user.live_tournament.title,
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
        current_user.live_tournament.full_web_directory,
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
            webroot=webroot(),
            title=current_user.live_tournament.title,
        )

        fn = os.path.join(round_dir, f"{r}.html")
        with open(fn, "w", encoding="utf-8") as f:
            f.write(html)

    return f"{games}", 200


@blueprint.route("/get_results")
@login_required
def update_ranking_and_scores():
    send_notifications = request.args.get("sendNotifications", "true") == "true"

    # Create a unique job ID
    job_id = str(uuid.uuid4())

    @copy_current_request_context
    def _finish_sheet_to_cloud():
        try:
            sheet = _get_sheet()
            schedule: dict = googlesheet.get_schedule(sheet)
            done: int = googlesheet.count_completed_hanchan(sheet)
            ranking = _ranking_to_cloud(sheet, done)
            players = _get_players(sheet, False)
            games = _games_to_cloud(sheet, done, players)
            _games_to_web(games, schedule, players)
            _ranking_to_web(ranking, games, players, done, schedule)
            if send_notifications:
                _message_player_topics(ranking, done, players)

            # Store completion status
            _store_job_status(job_id, "Scores updated successfully")
        except Exception as e:
            error_msg = f"Error updating scores: {str(e)}"
            logging.error(error_msg, exc_info=True)
            _store_job_status(job_id, error_msg)

    thread = threading.Thread(target=_finish_sheet_to_cloud)
    thread.start()

    return jsonify({"status": "processing", "job_id": job_id}), 202


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
def _games_to_cloud(sheet, done: int, players):
    results = {}
    for this_round in range(1, done + 1):
        one = _get_one_round_results(sheet, this_round)
        results.update(one)
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

    _save_to_cloud("scores", cleaned_scores, force_set=True)
    return results


@login_required
def _ranking_to_cloud(sheet, done: int) -> dict:
    results = googlesheet.get_results(sheet)
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
    _save_to_cloud("ranking", {round_index: all_scores, "roundDone": round_index})
    return all_scores


@login_required
def _get_players(sheet, to_cloud=True):
    raw: list[list] = googlesheet.get_players(sheet)
    players = []
    player_map = {}
    if len(raw) and len(raw[0]) > 2:
        # Find the highest seating_id
        max_seating_id = max((int(p[0]) for p in raw if p[0] != ""), default=0)

        for p in raw:
            registration_id = p[1]
            seating_id = p[0] if p[0] != "" else None
            name = p[2]
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
        _save_to_cloud("players", {"players": players})
    return player_map


@login_required
def _seating_to_map(sheet, schedule):
    raw = googlesheet.get_seating(sheet)
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


def _save_to_archive(document: str, data: dict, force_set=False):
    # For past tournaments, save to local database
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
def _save_to_cloud(document: str, data: dict, force_set=False):
    tournament = current_user.live_tournament

    if tournament.status == "past":
        return _save_to_archive()

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
