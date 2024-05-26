# -*- coding: utf-8 -*-
'''
pages and backend for the user running the tournament
'''
import json
import os
import threading

from firebase_admin import messaging
from flask import Blueprint, redirect, url_for, render_template, \
    copy_current_request_context, request
from flask_login import login_required, current_user

from create.write_sheet import googlesheet
from models import Access
from oauth_setup import db, firestore_client

blueprint = Blueprint('run', __name__)

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
def _publish_scores_on_web(scores, players, done: int):
    items = list(scores.items())
    sorted_scores = sorted(items, key=lambda item: item[1]['rank']) # sort by rank
    title = current_user.live_tournament.title
    html = render_template('scores.html',
                           title=title,
                           scores=sorted_scores,
                           done=done,
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
        return render_template('run_tournament.html')
    return redirect(url_for('create.index'))


@login_required
def _get_sheet():
    sheet_id = current_user.live_tournament_id
    return googlesheet.get_sheet(sheet_id)


@blueprint.route('/run/update_schedule')
@login_required
def update_schedule():
    sheet = _get_sheet()
    _schedule_to_cloud(sheet)
    _send_messages('schedule updated')
    return "SCHEDULE updated, notifications sent", 200


@blueprint.route('/run/update_seating')
@login_required
def update_seating():
    sheet = _get_sheet()
    schedule = _schedule_to_cloud(sheet)
    _seating_to_cloud(sheet, schedule)
    _send_messages('seating updated')
    return "SEATING PLAN updated, notifications sent", 200


@blueprint.route('/run/update_players')
@login_required
def update_players():
    sheet = _get_sheet()
    _players_to_cloud(sheet)
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
        name = players[k]
        _send_topic_fcm(
            f"{firebase_id}-{k}",
            f"{name} is now in position {('','=')[v['tied']]}{v['rank']}",
            f"with {v['total']} points after {done} round(s)",
            )

@login_required
def _get_one_game_results(sheet, scores: dict, rnd: int):
    vals = googlesheet.get_table_results(rnd, sheet)
    row : int = 4
    tables = {}
    while row + 3 < len(vals):
        # Get the table number from column 1
        table = vals[row][0]
        tables[table] = []
        if not table:
            # end of score page
            break
        # For each table, get the player ID & scores
        for i in range(4):
            player_id = vals[row + i][1]
            tables[table].append([
                player_id,                         # player_id: int
                round(10 * vals[row + i][3] or 0), # chombo: int
                round(10* vals[row + i][4]),       # game score: int
                vals[row + i][5],                  # placement: int
                round(10 * vals[row + i][6]),      # final score: int
                scores[player_id]['rank'],         # rank: int
                scores[player_id]['tied'],         # tied: int 0/1 pseudobool
                ])

        # Move to the next table
        row += 7
    return vals[0][1], tables


@login_required
def _games_to_cloud(sheet, scores : dict, done : int):
    all_games = []
    for i in range(1, done):
        name, results = _get_one_game_results(sheet, scores, i)
        all_games.append({'roundIndex': name, 'games': results})
    _save_to_cloud('games', all_games)
    return all_games


@login_required
def _publish_games_on_web(games, players): # TODO
    return f"{games}", 200


@blueprint.route('/run/get_results')
@login_required
def sheet_to_cloud():
    sheet = _get_sheet()
    done = googlesheet.count_completed_hanchan(sheet)
    scores = _scores_at_end_of_round(sheet, done)
    players = _players_to_cloud(sheet)

    @copy_current_request_context
    def _finish_sheet_to_cloud():
        schedule = _schedule_to_cloud(sheet)
        _seating_to_cloud(sheet, schedule)
        games = _games_to_cloud(sheet, scores, done)
        _publish_games_on_web(games, players)
        _message_player_topics(scores, done, players)

    thread = threading.Thread(target=_finish_sheet_to_cloud)
    thread.start()
    return _publish_scores_on_web(scores, players, done)


@login_required
def _scores_at_end_of_round(sheet, done : int) -> dict:
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

        all_scores[body[i][0]] = {
            "total": total,
            "penalties": round(body[i][4] * 10),
            "scores": [round(10 * s) for s in body[i][5 : 5 + done]],
            "rank": rank,
            "tied": tied,
            }

    return all_scores


@login_required
def _schedule_to_cloud(sheet):
    schedule: list(list) = googlesheet.get_schedule(sheet)
    _save_to_cloud('schedule', schedule)
    return schedule


@login_required
def _players_to_cloud(sheet):
    raw : list(list) = googlesheet.get_players(sheet)
    players = {int(p[0]): p[2] for p in raw}
    _save_to_cloud('players', players)
    return players


@login_required
def _seating_to_cloud(sheet, schedule):
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
                'tables': {},
                })
            hanchan_number = hanchan_number + 1
        seating[-1]['tables'][table] = players

    _save_to_cloud('seating', seating)
    # return seating


@login_required
def _save_to_cloud(key: str, data):
    firebase_id : str = current_user.live_tournament.firebase_doc
    ref = firestore_client.collection("tournaments")
    out : str = json.dumps(data, ensure_ascii=False, indent=None)
    ref.document(f"{firebase_id}/json/{key}").set(document_data={
        'json': out})
