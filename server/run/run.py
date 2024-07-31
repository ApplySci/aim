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
    copy_current_request_context, request, flash
from flask_login import login_required, current_user

from create.write_sheet import googlesheet
from models import Access, User, Tournament, Role
from oauth_setup import db, firestore_client
from run.userform import AddUserForm

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
def _ranking_to_web(scores, games, players, done, schedule):
    items = list(scores.items())
    sorted_scores = sorted(items, key=lambda item: item[1]['r']) # sort by rank
    title = current_user.live_tournament.title
    if done > 0:
        roundName = f"Scores after {schedule['rounds'][done-1]['name']}"
    else:
        roundName = 'End-of-round scores will appear here'
    html = render_template('projector.html',
                           title=title,
                           scores=sorted_scores,
                           round_name=roundName,
                           players=players,
                           webroot=webroot(),
                           )
    fn = os.path.join(
        current_user.live_tournament.web_directory,
        'projector.html')
    with open(fn, 'w', encoding='utf-8') as f:
        f.write(html)

    # ======================================

    scores_by_player = {}
    for r in range(1, done+1):
        rs = str(r)
        for t in games[rs]:
            for idx, line in games[rs][t].items():
                p = line[0]
                if p not in scores_by_player:
                    scores_by_player[p] = {}
                scores_by_player[p][r] = (line[4], t)
    html = render_template('ranking.html',
                           title=title,
                           scores=sorted_scores,
                           round_name=roundName,
                           players=players,
                           webroot=webroot(),
                           roundNames=_round_names(schedule),
                           done=done,
                           games=scores_by_player,
                           )
    fn = os.path.join(
        current_user.live_tournament.web_directory,
        'ranking.html')
    with open(fn, 'w', encoding='utf-8') as f:
        f.write(html)

    return 'ranking pages updated, notifications sent', 200


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
    # TODO allow the user to update the schedule on firebase WITHOUT seating
    if current_user.live_tournament:
        return render_template(
            'run_tournament.html',
            webroot=webroot(),
            )
    return redirect(url_for('run.select_tournament'))


@login_required
def _get_sheet():
    sheet_id = current_user.live_tournament.google_doc_id
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
    _seating_to_web(sheet=sheet, seating=seating)
    _send_messages('seating & schedule updated')
    return "SEATING & SCHEDULE updated, notifications sent", 200


@login_required
def _seating_to_web(sheet, seating):
    done : int = googlesheet.count_completed_hanchan(sheet)
    players = _get_players(sheet, False)
    schedule: dict = googlesheet.get_schedule(sheet)
    # TODO would be nice to get & show timezone

    html : str = render_template('seating.html',
        done=done,
        title=current_user.live_tournament.title,
        seating=seating,
        schedule=schedule,
        players=players,
        roundNames=_round_names(schedule),
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
                round(10 * vals[row + i][5] or 0), # chombo: int
                round(10* vals[row + i][3]),       # game score: int
                vals[row + i][4],                  # placement: int
                round(10 * vals[row + i][6]),      # final score: int
                ]

        # Move to the next table
        row += 7
    return {f"{rnd}": tables}

def webroot():
    start = "/static/"
    # TODO this crashes when we've just created the tournament,
    # as the web_directory is not yet set. Maybe fix the creation form
    # to set the web_directory. And check whether it already exists.
    result = current_user.live_tournament.web_directory.split(start, 1)[-1]
    return start + result

def _round_names(schedule):
    roundNames = {}
    for r in schedule['rounds']:
        roundNames[r['id']] = r['name']
    return roundNames

@login_required
def _games_to_web(games, schedule, players):
    roundNames = _round_names(schedule)
    player_dir = os.path.join(current_user.live_tournament.web_directory,
                              "players",)

    if not os.path.exists(player_dir):
        os.makedirs(player_dir)

    for pid, name in players.items():
        # for each player, create a page with all their games
        player_games = {}
        for r in games:
            for t in games[r]:
                present = False
                for p, s in games[r][t].items():
                    if s[0] == pid:
                        present = True
                        break
                if (present):
                    player_games[r] = {t: games[r][t]}

        html = render_template('player_page.html',
                               games=player_games,
                               players=players,
                               roundNames=roundNames,
                               done=len(games),
                               webroot=webroot(),
                               pid=pid,
                               title=current_user.live_tournament.title,
                               )

        fn = os.path.join(player_dir, f"{pid}.html")
        with open(fn, 'w', encoding='utf-8') as f:
            f.write(html)

    # =======================================================

    round_dir = os.path.join(current_user.live_tournament.web_directory,
                              "rounds",)

    if not os.path.exists(round_dir):
        os.makedirs(round_dir)

    for r in games:
        # for each round, create a page for all its games
        html = render_template('round_page.html',
                               games=games[r],
                               players=players,
                               roundNames=roundNames,
                               done=len(games),
                               roundname=roundNames[r],
                               webroot=webroot(),
                               title=current_user.live_tournament.title,
                               )

        fn = os.path.join(round_dir, f"{r}.html")
        with open(fn, 'w', encoding='utf-8') as f:
            f.write(html)

    return f"{games}", 200


@blueprint.route('/run/get_results')
@login_required
def update_ranking_and_scores():

    @copy_current_request_context
    def _finish_sheet_to_cloud():
        sheet = _get_sheet()
        schedule: dict = googlesheet.get_schedule(sheet)
        done : int = googlesheet.count_completed_hanchan(sheet)
        ranking = _ranking_to_cloud(sheet, done)
        players = _get_players(sheet, False)
        games = _games_to_cloud(sheet, done)
        _games_to_web(games, schedule, players)
        _ranking_to_web(ranking, games, players, done, schedule)
        _message_player_topics(ranking, done, players)

    thread = threading.Thread(target=_finish_sheet_to_cloud)
    thread.start()
    return "SCORES are being updated, and notifications sent, now", 200


@login_required
def _games_to_cloud(sheet, done: int):
    results = {}
    for this_round in range(1, done + 1):
        one = _get_one_round_results(sheet, this_round)
        results.update(one)
    _save_to_cloud('scores', results, force_set=True)
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
def _save_to_cloud(document: str, data: dict, force_set = False):
    firebase_id : str = current_user.live_tournament.firebase_doc
    ref = firestore_client.collection("tournaments").document(
        f"{firebase_id}/v2/{document}")

    doc = ref.get()
    if doc.exists and not force_set:
        # If the document exists, update the field
        ref.update(data)
    else:
        # If the document does not exist, create it with the field
        ref.set(data)

@blueprint.route('/run/add_user', methods=['POST'])
@login_required
def add_user_post():
    form = AddUserForm(request.form)
    tournaments = current_user.get_tournaments(db.session)
    form.tournament.choices = [(t.id, t.title) for t in tournaments]

    if not form.validate_on_submit():
        return add_user_get()

    email = form.email.data
    tournament_id = form.tournament.data
    role = form.role.data

    # Check if the user already exists
    user = db.session.query(User).filter_by(email=email).first()
    if not user:
        user = User(email=email)
        db.session.add(user)
        db.session.commit()

    # Add the user to the tournament with the specified role
    access = db.session.query(Access).filter_by(
            user_email=email, tournament_id=tournament_id).first()
    if not access:
        tournament = db.session.query(Tournament).get(tournament_id)
        access = Access(user=user, tournament=tournament, role=Role[role])
        db.session.add(access)
        db.session.commit()
        share_result = googlesheet.share_sheet(
                tournament.google_doc_id, email, notify=False)
        if share_result == True:
            flash('Scorer added successfully!', 'success')
        else:
            flash(f'Failed to add scorer: {share_result}', 'danger')
    else:
        flash('Scorer is already attached this tournament.', 'success')

    return redirect(url_for('run.run_tournament'))

@blueprint.route('/run/add_user', methods=['GET'])
@login_required
def add_user_get():
    tournaments = current_user.get_tournaments(db.session)
    tournament_choices = [(str(t.id), t.title) for t in tournaments]
    
    form = AddUserForm(request.form)
    form.tournament.choices = tournament_choices
    
    if current_user.live_tournament_id:
        form.tournament.data = str(current_user.live_tournament_id)
    
    return render_template('add_user.html', form=form)
