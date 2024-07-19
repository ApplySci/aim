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
from .cloud_edit import TournamentForm
from oauth_setup import db, firestore_client
from config import GOOGLE_CLIENT_EMAIL
from models import Access, Role, Tournament

blueprint = Blueprint('create', __name__)
messages_by_user = {}


@blueprint.route('/create/')
def index():
    if current_user.is_authenticated:
        return render_template('welcome_admin.html')
    else:
        return render_template('welcome_anon.html')


@blueprint.route('/create/results', methods=['GET', 'POST', 'PUT'])
@login_required
def results_create():
    owner = current_user.email
    form = GameParametersForm()
    if not form.validate_on_submit():
        return render_template('create_results.html', form=form)

    tournament : Tournament = Tournament(title=form.title.data)
    hanchan_count = int(form.hanchan_count.data)
    round_name_template = form.other_name.data if \
        form.hanchan_name.data == 'other' \
        else form.hanchan_name.data
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
            round_name_template=round_name_template,
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
    # TODO add to the firebase database too!
    # and then add the database document ID to our local db here
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


@blueprint.route('/create/metadata', methods=['POST'])
@login_required
def update_tournament():
    docId = current_user.live_tournament.firebase_doc or 'None'
    doc_ref = firestore_client.collection('tournaments').document(docId)
    form = TournamentForm(request.form)
    if not form.validate_on_submit():
        print('cloud_edit form failed validation')
        return render_template('cloud_edit.html', form=form)
    if docId == None:
        # TODO create doc
        print('no docId present')
    doc_ref.set({
        'start_date': form.start_date.data,
        'end_date': form.end_date.data,
        'address': form.address.data,
        'country': form.country.data,
        'name': form.name.data,
        'status': form.status.data,
        'url': form.url.data,
        'url_icon': form.url_icon.data
    })
    return render_template('cloud_edit.html', form=form)

@blueprint.route('/create/metadata', methods=['GET'])
@login_required
def edit_tournament():
    sheet = googlesheet.get_sheet(current_user.live_tournament_id)
    schedule = googlesheet.get_schedule(sheet)
    docId = current_user.live_tournament.firebase_doc or 'None'
    doc_ref = firestore_client.collection('tournaments').document(docId)
    doc = doc_ref.get()
    form = TournamentForm()
    if doc.exists:
        data = doc.to_dict()
        form.start_date.data = data['start_date']
        form.end_date.data = data['end_date']
        form.address.data = data['address']
        form.country.data = data['country']
        form.name.data = data['name']
        form.status.data = data['status']
        form.url.data = data.get('url', '')
        form.url_icon.data = data.get('url_icon', '')
    else:
        # get start and end date from schedule
        form.tournament.data = current_user.live_tournament.title

    return render_template('cloud_edit.html', form=form)
