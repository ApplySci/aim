# -*- coding: utf-8 -*-

import os

from authlib.integrations.flask_client import OAuth
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from firebase_admin import credentials, initialize_app as initialize_firebase
from firebase_admin import firestore

from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, DEFAULT_USERS
from models import User, Tournament, Access, Role

oauth = OAuth()
login_manager = LoginManager()
db = SQLAlchemy()

app_directory = os.path.dirname(os.path.realpath(__file__))
KEYFILE = os.path.join(app_directory, 'fcm-admin.json')

initialize_firebase(credentials.Certificate(KEYFILE))
firestore_client = firestore.client()


def config_db(app):

    # Get the directory of the current file
    db_file = "tournaments.sqlite3"

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
        os.path.join(app_directory, db_file)

    db.init_app(app)
    with app.app_context():
        # ensure our defaults are in place
        scoresheet_ids = (
            '1kTAYPtyX_Exl6LcpyCO3-TOCr36Mf-w8z8Jtg_O6Gw8',
            '1wbxTZJnF-CE90xYEk34z9WgDjawdbHbW_Rb8fQ9yd6A',
            )
        firebase_docs = (
            'Y3sDqxajiXefmP9XBTvY',
            'test2',
            )
        webdirs = (
            '/home/model/apps/tournaments/myapp/static/',
            '/home/model/apps/tournaments/myapp/static/wr/',
            )
        titles = (
            'Irish Riichi Open, Cork 2024',
            'World Riichi App - demo tournament for testing',
            )
        addresses = (
            'The Crows Nest, Victoria Cross Road, Cork, Ireland',
            'Grimsby Dock Tower, Wharncliffe Rd N, Grimsby DN31 3QL, UK',
            )

        for email in DEFAULT_USERS:
            if not db.session.query(User).get(email):
                db.session.add(User(email=email))
        db.session.commit()

        for i in range(2):
            if not db.session.query(Tournament).get(scoresheet_ids[i]):
                t = Tournament(
                    id=scoresheet_ids[i],
                    title=titles[i],
                    web_directory=webdirs[i],
                    firebase_doc=firebase_docs[i],
                    address=addresses[i],
                    )
                db.session.add(t)
                for email in DEFAULT_USERS:
                    db.session.add(Access(
                        user_email=email,
                        tournament_id=scoresheet_ids[i],
                        role=Role.admin,
                        ))
                db.session.commit()


def config_jinja(app):
    def prettyScore(score: int):
        if score < 0:
            prefix = '-'
        elif score > 0:
            prefix = '+'
        else:
            prefix = ''
        return f"{prefix}{(abs(round(score/10, 1)))}"
    env = app.jinja_env
    env.filters['prettyScore'] = prettyScore

def config_login_manager(app):
    login_manager.init_app(app)
    login_manager.login_view = '/login'

def config_oauth(app):
    oauth.init_app(app)
    oauth.register(
        'google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        access_token_url='https://accounts.google.com/o/oauth2/token',
        access_token_params=None,
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        authorize_params=None,
        api_base_url='https://www.googleapis.com/oauth2/v1/',
        client_kwargs={'scope': 'email',},
    )
