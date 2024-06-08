# -*- coding: utf-8 -*-
'''
pages and backend for the user running the tournament
'''
from functools import wraps
import os
import sys
import threading
import traceback

from firebase_admin import messaging
from flask import Blueprint, redirect, url_for, render_template, \
    copy_current_request_context, request
from flask_login import login_required, current_user

from create.write_sheet import googlesheet
from models import Access
from oauth_setup import db, firestore_client

blueprint = Blueprint('run', __name__)

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


@blueprint.route('/run/select_tournament', methods=['GET', 'POST',])
@login_required
def select_tournament():
    new_id = request.form.get('id')
    if new_id:
        current_user.live_tournament_id = new_id
        db.session.commit()
        return redirect(url_for('run.run_tournament'))
    # Query the Access table for all records where the user_email is the current user's email
    accesses = db.session.query(Access).filter_by(
        user_email=current_user.email).all()
    tournaments = [access.tournament for access in accesses]
    return render_template('select_tournament.html', tournaments=tournaments)


@login_required
def _publish_ranking_on_web(scores, players, done, round_name):
    items = list(scores.items())
    sorted_scores = sorted(items, key=lambda item: item[1]['r']) # sort by rank
    title = current_user.live_tournament.title
    print(players)
    print(sorted_scores)
    html = render_template('scores.html',
                           title=title,
                           scores=sorted_scores,
                           round_name=round_name,
                           players=players,
                           )
    fn = os.path.join(
        current_user.live_tournament.web_directory,
        'scores.html')
    with open(fn, 'w', encoding='utf-8') as f:
        f.write(html)

    return 'scores.html has been updated, notifications sent', 200


@login_required
def _send_topic_fcm(topic: str, title: str, body: str):
    message = messaging.Message(
        notification = messaging.Notification(title=title,body=body,),
        topic=topic,  # The topic name
        )
    messaging.send(message)


@blueprint.route('/run/')
@login_required
def run_tournament():
    if current_user.live_tournament:
        # TODO current_user.live_tournament.web_directory
        #   but that gives /home/model/apps/tournaments/myapp/static/wr
        return render_template(
            'run_tournament.html',
            webroot='/static/wr',
            )
    return redirect(url_for('create.index'))


@login_required
def _get_sheet():
    sheet_id = current_user.live_tournament_id
    return googlesheet.get_sheet(sheet_id)


@blueprint.route('/run/update_schedule')
@wrap_and_catch
@login_required
def update_schedule():
    sheet = _get_sheet()
    schedule: dict = googlesheet.get_schedule(sheet)
    seating = _seating_to_map(sheet, schedule)
    _save_to_cloud('seating', {
        'rounds': seating,
        'timezone': schedule['timezone'],
        })
    _publish_seating_on_web(sheet=sheet, seating=seating)
    _send_messages('seating & schedule updated')
    return "SEATING & SCHEDULE updated, notifications sent", 200


@login_required
def _publish_seating_on_web(sheet, seating): # TODO
    done : int = googlesheet.count_completed_hanchan(sheet)
    players = _get_players(sheet, False)
    schedule_vals = googlesheet.get_raw_schedule(sheet)

    html : str = render_template('seating.html',
        done=done,
        timezone=schedule_vals[0][2],
        title=current_user.live_tournament.title,
        seating=seating,
        schedule=schedule_vals[2:],
        players=players,
        )
    fn = os.path.join(
        current_user.live_tournament.web_directory,
        'seating.html')
    with open(fn, 'w', encoding='utf-8') as f:
        f.write(html)
    return "Seating published on web", 200


@blueprint.route('/run/update_players')
@wrap_and_catch
@login_required
def update_players():
    sheet = _get_sheet()
    _get_players(sheet, True)
    _send_messages('player list updated')
    return "PLAYERS updated, notifications sent", 200


@login_required
def _send_messages(msg: str):
    '''
    '''
    firebase_id = current_user.live_tournament.firebase_doc
    _send_topic_fcm(firebase_id, msg, current_user.live_tournament.title)


@login_required
def _message_player_topics(scores: dict, done: int, players):
    '''
    send all our player-specific firebase notifications out
    do this in a separate thread so as not to hold up the main response
    '''
    firebase_id = current_user.live_tournament.firebase_doc
    for k,v in scores.items():
        name = players[int(k)]
        _send_topic_fcm(
            f"{firebase_id}-{k}",
            f"{name} is now in position {('','=')[v['t']]}{v['r']}",
            f"with {v['total']} points after {done} round(s)",
            )

@login_required
def _get_one_round_results(sheet, rnd: int):
    vals = googlesheet.get_table_results(rnd, sheet)
    row : int = 4
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
            tables[table][f"{i}"] = [
                player_id,                         # player_id: int
                round(10 * vals[row + i][3] or 0), # chombo: int
                round(10* vals[row + i][4]),       # game score: int
                vals[row + i][5],                  # placement: int
                round(10 * vals[row + i][6]),      # final score: int
                ]

        # Move to the next table
        row += 7
    return {f"{rnd}": tables}


@login_required
def _publish_games_on_web(games, schedule, players): # TODO
    return f"{games}", 200


@blueprint.route('/run/get_results')
@login_required
def update_ranking_and_scores():

    @copy_current_request_context
    def _finish_sheet_to_cloud():
        sheet = _get_sheet()
        schedule: dict = googlesheet.get_schedule(sheet)
        done : int = googlesheet.count_completed_hanchan(sheet)
        round_name : str = schedule['rounds'][done-1]['name']
        ranking = _ranking_to_cloud(sheet, done)
        players = _get_players(sheet, False)
        games = _games_to_cloud(sheet, done)
        _publish_games_on_web(games, schedule, players)
        _publish_ranking_on_web(ranking, players, done, round_name)
        _message_player_topics(ranking, done, players)

    thread = threading.Thread(target=_finish_sheet_to_cloud)
    thread.start()
    return "SCORES are being updated, and notifications sent, now", 200


@login_required
def _games_to_cloud(sheet, this_round: int):
    results = _get_one_round_results(sheet, this_round)
    _save_to_cloud('scores', results)
    return results


@login_required
def _ranking_to_cloud(sheet, done : int) -> dict:
    results = googlesheet.get_results(sheet)
    body = results[1:]
    body.sort(key=lambda x: -x[3]) # sort by descending cumulative score
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

    round_index : str = f"{done}"
    _save_to_cloud('ranking', {
        round_index: all_scores,
        'roundDone': round_index
        })
    return all_scores


@login_required
def _get_players(sheet, to_cloud=True):
    raw : list(list) = googlesheet.get_players(sheet)
    if len(raw) and len(raw[0]) > 2:
        players = [{'id': p[0], 'name': p[2]} for p in raw]
        player_map = {p[0]: p[2] for p in raw}
    else:
        players = []
        player_map = {}
    if to_cloud:
        _save_to_cloud('players', {'players': players})
    return player_map


@login_required
def _seating_to_map(sheet, schedule):
    raw = googlesheet.get_seating(sheet)
    seating = []
    previous_round = ''
    hanchan_number = 0
    for t in raw:
        this_round = str(t[0])
        table = str(t[1])
        players = t[2:]
        if this_round != previous_round:
            previous_round = this_round
            seating.append({
                'id': this_round,
                'name': schedule['rounds'][hanchan_number]['name'],
                'start': schedule['rounds'][hanchan_number]['start'],
                'tables': {},
                })
            hanchan_number = hanchan_number + 1
        seating[-1]['tables'][table] = players

    return seating


@login_required
def _save_to_cloud(document: str, data: dict):
    firebase_id : str = current_user.live_tournament.firebase_doc
    ref = firestore_client.collection("tournaments").document(
        f"{firebase_id}/v2/{document}")

    doc = ref.get()
    if doc.exists:
        # If the document exists, update the field
        ref.update(data)
    else:
        # If the document does not exist, create it with the field
        ref.set(data)
