# -*- coding: utf-8 -*-
'''
creates the front-end pages for the user to set up a new google scoresheet.

Sigh. We're really going to need a database here, at least to store their
login id and their sheet id.
'''
import threading

from flask import Blueprint, jsonify, redirect, url_for, session, \
    render_template, current_app
from flask_login import UserMixin, login_required, login_user, logout_user, \
    current_user

from .write_sheet import googlesheet
from .form_create_results import GameParametersForm
from oauth_setup import oauth, login_manager
from config import ALLOWED_USERS, GOOGLE_CLIENT_EMAIL, OUR_EMAILS, TEMPLATE_ID

create_blueprint = Blueprint('create', __name__)
messages_by_user = {}

login_manager.login_view = 'index'

class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email


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
            title=f"copy {form.title.data}",
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
    return redirect(url_for('create.select_sheet'))


@create_blueprint.route('/create/admin')
@login_required
def superuser():
    if session['email'] not in OUR_EMAILS:
        return "not found",  404
    docs = googlesheet.list_sheets(GOOGLE_CLIENT_EMAIL)
    our_docs = [doc for doc in docs if doc['ours'] and \
                doc['id'] != TEMPLATE_ID]
    return render_template('adminlist.html', docs=our_docs)


@create_blueprint.route('/create/delete/<doc_id>', methods=['DELETE',])
@login_required
def delet_dis(doc_id):
    if session['email'] not in OUR_EMAILS:
        return "not found",  404
    googlesheet.delete_sheet(doc_id)
    return "ok", 204


@create_blueprint.route('/create/is_sheet_created')
@login_required
def poll_new_sheet():
    messages = messages_by_user.get(session['email'])
    if messages:
        for message in messages:
            current_app.logger.warning(f'in poll_new_sheet with {message}')
            if message['ours']:
                current_app.logger.warning('sending it!')
                return jsonify(message)

    return "not ready yet", 204


@create_blueprint.route('/create/copy_made')
@login_required
def get_their_copy():
    owner = session['email']
    docs = googlesheet.list_sheets(owner)
    their_docs = []
    for doc in docs:
        if not doc['ours']:
            their_docs.append(doc)
    if (their_docs):
        return jsonify(their_docs)
    return "none found", 204


@create_blueprint.route('/create/select_sheet', methods=['GET', 'POST', 'PUT'])
@login_required
def select_sheet():
    docs = messages_by_user.get(session['email'])
    return render_template(
        'sheet_wip.html',
        docs=docs,
        OUR_EMAIL=GOOGLE_CLIENT_EMAIL,
        )
