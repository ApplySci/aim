# -*- coding: utf-8 -*-
'''
creates the front-end pages for the user to set up a new google scoresheet
'''
import json
import threading
import time

from flask import Blueprint, jsonify, redirect, url_for, session, \
    render_template, stream_with_context, Response, current_app
from flask_login import UserMixin, login_required, login_user, logout_user, \
    current_user

from .write_sheet import googlesheet
from .form_create_results import GameParametersForm
from oauth_setup import oauth, login_manager
from config import ALLOWED_USERS

create_blueprint = Blueprint('create', __name__)
messages_by_user = {}

class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email


@stream_with_context
def event_stream():
   '''
   Watch for messages stacked in the module variable, keyed to this user.
   Send them over the Server-Side Events connection
   '''
   last_seen_id = -1
   while True:
       messages = messages_by_user.get(session['email'])
       while messages and len(messages) > last_seen_id + 1:
           current_app.logger.warning(f'trying to yield {messages[last_seen_id + 1]}')
           yield 'data: {}\n\n'.format(messages[last_seen_id + 1])
           last_seen_id += 1
       time.sleep(10)


@login_required
@create_blueprint.route('/create/stream')
def stream():
    return Response(event_stream(), mimetype="text/event-stream")


@login_manager.user_loader
def load_user(user_id):
    if 'email' in session:
        return User(session['email'], session['id'])
    return None


@create_blueprint.route('/create/')
def index():
    if current_user.is_authenticated:
        return render_template('welcome_admin.html')
    else:
        return render_template('welcome_anon.html')


@create_blueprint.route('/create/login')
def login():
    redirect_uri = url_for('create.authorized', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@create_blueprint.route('/create/logout')
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('create.index'))


@create_blueprint.route('/auth/')
def authorized():
    # we're not going to use the token outside this call, so we don't
    #     need to save it to a variable here
    oauth.google.authorize_access_token()
    resp = oauth.google.get('userinfo')
    user_info = resp.json()
    email = user_info['email']
    if email not in ALLOWED_USERS:
        return logout()

    session['email'] = email
    this_id = session['id'] = user_info['id'] # obfuscated google user id
    user = User(this_id, email)
    login_user(user)
    return redirect(url_for('create.index'))


@create_blueprint.route('/create/results', methods=['GET', 'POST', 'PUT'])
@login_required
def results_create():
    owner = session['email']
    form = GameParametersForm()
    if not form.validate_on_submit():
        return render_template('create_results.html', form=form)

    def make_sheet():
        sheet_id : str = googlesheet.create_new_results_googlesheet(
            table_count=form.table_count.data,
            hanchan_count=form.game_count.data,
            title=form.title.data,
            owner=owner,
            scorers=form.emails.data.split(','),
            notify=form.notify.data,
        )
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
    return redirect(url_for('create.set_id')) # render_template('sheet_wip.html')


@create_blueprint.route('/create/copy_made')
@login_required
def poll_sheetlist():
    owner = session['email']
    def get_list():
        docs = googlesheet.list_sheets(owner)
        msgs = messages_by_user.get(owner)
        if not msgs:
            messages_by_user[owner] = []
        for doc in docs:
            messages_by_user[owner].append(doc)
        return docs

    #thread = threading.Thread(target=get_list)
    #thread.start()

    return jsonify(get_list()) # "OK", 200


@create_blueprint.route('/create/select_sheet', methods=['GET', 'POST', 'PUT'])
@login_required
def select_sheet():
    docs = messages_by_user.get(session['email'])
    return render_template('sheet_wip.html', docs=docs)
