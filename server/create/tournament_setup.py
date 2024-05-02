# -*- coding: utf-8 -*-
'''
creates the front-end pages for the user to set up a new google scoresheet.
'''
import threading

from flask import Blueprint, jsonify, redirect, request, url_for, \
    render_template, current_app, copy_current_request_context
from flask_login import login_required, current_user

from .write_sheet import googlesheet
from .form_create_results import GameParametersForm
from oauth_setup import db, login_manager
from config import GOOGLE_CLIENT_EMAIL
from models import Access, Role, Tournament, User

blueprint = Blueprint('create', __name__)
messages_by_user = {}


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


@blueprint.route('/create/')
def index():
    if current_user.is_authenticated:
        return render_template('welcome_admin.html')
    else:
        return render_template('welcome_anon.html')


@blueprint.route('/create/run')
@login_required
def run_tournament():
    if hasattr(current_user, 'tournament'):
        return render_template('run_tournament.html')
    return redirect(url_for('create.index'))


@blueprint.route('/create/results', methods=['GET', 'POST', 'PUT'])
@login_required
def results_create():
    owner = current_user.email
    form = GameParametersForm()
    if not form.validate_on_submit():
        return render_template('create_results.html', form=form)

    tournament : Tournament = Tournament(title=form.title.data)
    hanchan_count = int(form.hanchan_count.data)
    start_times = [request.form.get(f'round{i}') for i in
                   range(1, 1 + hanchan_count)]


    @copy_current_request_context
    def make_sheet():
        sheet_id : str = googlesheet.create_new_results_googlesheet(
            table_count=int(form.table_count.data),
            hanchan_count=hanchan_count,
            title=f"copy {form.title.data}",
            owner=owner,
            scorers=form.emails.data.split(','),
            notify=form.notify.data,
            timezone=form.timezone.data,
            start_times=start_times,
        )
        tournament.id = sheet_id

        msg = messages_by_user.get(owner)
        if not msg:
            messages_by_user[owner] = []
        messages_by_user[owner].append({
            'id': sheet_id,
            'title': form.title.data,
            'ours': True,
            })

    thread = threading.Thread(target=make_sheet)
    thread.start()
    return redirect(url_for('create.select_sheet'))


@blueprint.route('/create/is_sheet_created')
@login_required
def poll_new_sheet():
    messages = messages_by_user.get(current_user.email)
    if messages:
        for message in messages:
            current_app.logger.warning(f'in poll_new_sheet with {message}')
            if message['ours']:
                current_app.logger.warning('sending it!')
                return jsonify(message)

    return "not ready yet", 204


@blueprint.route('/create/copy_made')
@login_required
def get_their_copy():
    docs = googlesheet.list_sheets(current_user.email)
    their_docs = []
    for doc in docs:
        if not doc['ours']:
            their_docs.append(doc)
    if (their_docs):
        return jsonify(their_docs)
    return "none found", 204


@blueprint.route('/create/select/<doc>', methods=['POST', 'GET', 'PUT'])
@login_required
def google_doc_selected(doc):
    title = request.form.get('submit')
    _add_to_db(doc, title)
    current_user.live_tournament_id = doc
    db.session.commit()
    return redirect(url_for('run.run_tournament'))


@blueprint.route('/create/select_sheet', methods=['GET', 'POST', 'PUT'])
@login_required
def select_sheet():
    docs = messages_by_user.get(current_user.email)
    return render_template(
        'sheet_wip.html',
        docs=docs,
        OUR_EMAIL=GOOGLE_CLIENT_EMAIL,
        )


def _add_to_db(id, title):
    tournament = db.session.query(Tournament).get(id)
    if not tournament :
        tournament = Tournament(id=id, title=title)
        db.session.add(tournament)

    access = db.session.query(Access).filter_by(
        user_email=current_user.email,
        tournament_id=id,
        ).first()
    if not access:
        access = Access(user=current_user, tournament=tournament, role=Role.admin)
        db.session.add(access)
    db.session.commit()
    return tournament
