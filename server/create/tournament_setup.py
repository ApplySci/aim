# -*- coding: utf-8 -*-
'''
creates the front-end pages for the user to set up a new google scoresheet
'''
import functools
import threading

from flask import Blueprint, jsonify, redirect, url_for, session, \
    render_template
from flask_login import UserMixin, login_required, login_user, logout_user, \
    current_user
from flask_socketio import disconnect, emit

from .write_sheet import googlesheet
from .form_create_results import GameParametersForm
from .form_set_tournament import PickTournament
from oauth_setup import oauth, login_manager, socketio
from config import ALLOWED_USERS

create_blueprint = Blueprint('create', __name__)
doc_ids = {}
previous_doc_ids = {}

class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email

def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped

dummy = """
#@authenticated_only
@socketio.on('connect')
def create_connect():
    print('*****      Client connected')
    emit('my_event', { "data": "i'm connected" }, )


#@authenticated_only
@socketio.on('get_sheets')
def handle_my_custom_event(data):
    emit('my response', {}, broadcast=True) # doc_ids
"""

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
    doc_ids[email] = {'ours': [], 'theirs': [], 'live': None}
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
        googlesheet.create_new_results_googlesheet(
            table_count=form.table_count.data,
            hanchan_count=form.game_count.data,
            title=form.title.data,
            owner=owner,
            scorers=form.emails.data.split(','),
            notify=form.notify.data,
        )
        doc_ids[owner]['ours'].append(googlesheet.live_sheet.id)

    thread = threading.Thread(target=make_sheet)
    thread.start()
    return redirect(url_for('create.set_id')) # render_template('sheet_wip.html')


@create_blueprint.route('/create/poll_sheetlist')
@login_required
def poll_sheetlist():
    doc_ids = googlesheet.list_sheets(session['email'])
    # TODO test if this differs in contents from previous_doc_ids


    return jsonify(doc_ids)


@create_blueprint.route('/create/select_sheet', methods=['GET', 'POST', 'PUT'])
@login_required
def select_sheet():
    form = PickTournament()
    if not form.validate_on_submit():
        return render_template(
            'sheet_wip.html',
            form=form,
            docs=googlesheet.list_sheets(session['email']),
            )

    return render_template('sheet_wip.html')
