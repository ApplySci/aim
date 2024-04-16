# -*- coding: utf-8 -*-

import os

from authlib.integrations.flask_client import OAuth
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from firebase_admin import credentials, initialize_app as initialize_firebase
from firebase_admin import firestore

from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, DEFAULT_USERS, DEFAULT_OWNER
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
        scoresheet_id = '1kTAYPtyX_Exl6LcpyCO3-TOCr36Mf-w8z8Jtg_O6Gw8'
        firebase_doc = 'Y3sDqxajiXefmP9XBTvY'
        for email in DEFAULT_USERS:
            if not db.session.query(User).get(email):
                db.session.add(User(email=email))
        db.session.commit()

        if not db.session.query(Tournament).get(scoresheet_id):
            t = Tournament(
                id=scoresheet_id,
                our_template_id='',
                title='Cork 2024',
                outdir='',
                firebase_doc=firebase_doc,
                )
            db.session.add(t)
            db.session.add(Access(
                user_email=DEFAULT_OWNER,
                tournament_id=scoresheet_id,
                role=Role.admin,
                ))
            db.session.add(Access(
                user_email=DEFAULT_USERS[2],
                tournament_id=scoresheet_id,
                role=Role.admin,
                ))
            db.session.commit()


def config_login_manager(app):
    login_manager.init_app(app)

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
