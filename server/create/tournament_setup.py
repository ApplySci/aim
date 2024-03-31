# -*- coding: utf-8 -*-

from flask import Blueprint, redirect, url_for, session, render_template
from flask_login import UserMixin, login_required

from .write_sheet import GSP
from .create_results import GameParametersForm
from oauth_setup import oauth

# login_manager = LoginManager()
# login_manager.init_app(current_app)

create_blueprint = Blueprint('create', __name__)

class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email


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
    session.pop('email', None)
    return redirect(url_for('create.index'))

@create_blueprint.route('/create/authorized')
def authorized(resp):
    # we're not going to use the token outside this call, so we don't
    #     need to save it to a variable here
    oauth.google.authorize_access_token()

    resp = oauth.google.get('userinfo')
    user_info = resp.json()
    session['email'] = user_info['email']
    return redirect(url_for('create.index'))


@create_blueprint.route('/create/results', methods=['GET', 'POST', 'PUT'])
#@login_required
def results_create():
    form = GameParametersForm()
    if not form.validate_on_submit():
        return render_template('create_results.html', form=form)

    gsp = GSP()
    sheet = gsp.create_new_results_googlesheet(
        table_count=form.table_count.data,
        hanchan_count=form.game_count.data,
        title=form.title.data,
        owner=session['email'],
        scorers=form.emails.data.split(','),
        notify=form.notify.data,
    )

    return f'Form submitted successfully: new id is {sheet.id}'
