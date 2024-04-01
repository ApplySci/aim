# -*- coding: utf-8 -*-
'''
creates the front-end pages for the user to set up a new google scoresheet
'''

import threading

from flask import Blueprint, redirect, url_for, session, render_template
from flask_login import UserMixin, login_required, login_user, logout_user

from .write_sheet import GSP
from .form_create_results import GameParametersForm
from oauth_setup import oauth, login_manager

create_blueprint = Blueprint('create', __name__)


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
    if 'email' in session:
        return render_template('create_results.html', email=session['email'])
    else:
        return redirect(url_for('create.login'))


@create_blueprint.route('/create/login')
def login():
    redirect_uri = url_for('create.authorized', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@create_blueprint.route('/create/logout')
def logout():
    logout_user()
    session.pop('email', None)
    return redirect(url_for('create.index'))


@create_blueprint.route('/auth/')
def authorized(resp):
    # we're not going to use the token outside this call, so we don't
    #     need to save it to a variable here
    oauth.google.authorize_access_token()

    resp = oauth.google.get('userinfo')
    user_info = resp.json()
    session['email'] = user_info['email']
    return redirect(url_for('create.index'))

    session['email'] = user_info['email']
    session['id'] = user_info['id'] # obfuscated google user id
    user = User(user_info['id'], user_info['email'])
    login_user(user)
    return redirect(url_for('hello_world'))


@create_blueprint.route('/create/results', methods=['GET', 'POST', 'PUT'])
@login_required
def results_create():
    owner = session['email'] # = 'mj.apply.sci@gmail.com'
    form = GameParametersForm()
    if not form.validate_on_submit():
        return render_template('create_results.html', form=form)

    def make_sheet():
        gsp = GSP()
        gsp.create_new_results_googlesheet(
            table_count=form.table_count.data,
            hanchan_count=form.game_count.data,
            title=form.title.data,
            owner=owner,
            scorers=form.emails.data.split(','),
            notify=form.notify.data,
        )
        print(f"***  finished creating spreadsheet {gsp.live_sheet.id}")

    thread = threading.Thread(target=make_sheet)
    thread.start()
    return render_template('sheet_wip.html')
