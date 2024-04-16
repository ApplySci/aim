# -*- coding: utf-8 -*-
'''
pages and backend for the user running the tournament
'''
import json

from firebase_admin import messaging
from flask import Blueprint, redirect, url_for, render_template
from flask_login import login_required, current_user

from create.write_sheet import googlesheet
from oauth_setup import db, firestore_client
from models import Access

blueprint = Blueprint('run', __name__)
messages_by_user = {}


@login_required
def _send_topic_fcm(topic: str, title: str, body: str):
    message = messaging.Message(
        notification = messaging.Notification(title=title,body=body,),
        topic=topic,  # The topic name
        )
    response = messaging.send(message)
    print('Successfully sent message:', response)


@blueprint.route('/run')
@login_required
def run_tournament():
    if hasattr(current_user, 'tournament'):
        return render_template('run_tournament.html')
    return redirect(url_for('create.index'))


@blueprint.route('/run/select_tournament', methods=['GET', 'POST',])
@login_required
def select_tournament():
    # Query the Access table for all records where the user_email is the current user's email
    accesses = db.session.query(Access).filter_by(
        user_email=current_user.email).all()
    tournaments = [access.tournament for access in accesses]
    return render_template('select_tournament.html', tournaments=tournaments)


@blueprint.route('/run/get_results')
@login_required
def sheet_to_cloud():
    # TODO send notifications
    _scores_to_cloud()
    _players_to_cloud()
    _seating_to_cloud()
    return 'data has been stored in the cloud', 200


@login_required
def _scores_to_cloud():
    # TODO don't hardcode sheet id
    sheet = googlesheet.get_sheet('1kTAYPtyX_Exl6LcpyCO3-TOCr36Mf-w8z8Jtg_O6Gw8') # current_user.live_tournament_id)
    done, results = googlesheet.get_results(sheet)
    body = results[1:]
    body.sort(key=lambda x: -x[3]) # sort by descending cumulative score
    all_scores = []
    previous_score = -99999
    for i in range(len(body)):
        total = round(10 * body[i][3])
        if previous_score == total:
            prefix = '='
        else:
            previous_score = total
            rank = i + 1
            prefix = ''

        all_scores.append({
            "id": body[i][0],
            "t": total,
            "r": f'{prefix}{rank}',
            "p": round(body[i][4] * 10),
            "s": [round(10 * s) for s in body[i][5 : 5 + done]],
            })

    all_scores[0]['roundDone'] = done
    out : str = json.dumps(all_scores, ensure_ascii=False, indent=None)
    _save_to_cloud('scores', out)


@login_required
def _players_to_cloud():
    # TODO don't hardcode sheet id
    sheet = googlesheet.get_sheet('1kTAYPtyX_Exl6LcpyCO3-TOCr36Mf-w8z8Jtg_O6Gw8') # current_user.live_tournament_id)
    raw : list(list) = googlesheet.get_players(sheet)
    players = {int(p[0]): p[2] for p in raw}
    out : str = json.dumps(players, ensure_ascii=False, indent=None)
    _save_to_cloud('players', out)


@login_required
def _seating_to_cloud():
    # TODO don't hardcode sheet id
    sheet = googlesheet.get_sheet('1kTAYPtyX_Exl6LcpyCO3-TOCr36Mf-w8z8Jtg_O6Gw8') # current_user.live_tournament_id)
    raw = googlesheet.get_seating(sheet)
    schedules = googlesheet.get_schedule(sheet)
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
                'start': schedules[hanchan_number][1],
                'tables': {},
                })
            hanchan_number = hanchan_number + 1
        seating[-1]['tables'][table] = players
    out : str = json.dumps(seating, ensure_ascii=False, indent=None)
    _save_to_cloud('seating', out)


@login_required
def _save_to_cloud(key: str, data: str):
    # TODO just for testing - stuff shouldn't be hardcoded here
    firebase_id : str = 'Y3sDqxajiXefmP9XBTvY' # current_user.live_tournament.firebase_doc
    ref = firestore_client.collection("tournaments")
    ref.document(f"{firebase_id}/json/{key}").set(document_data={
        'json': data})
