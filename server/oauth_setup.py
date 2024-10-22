# -*- coding: utf-8 -*-

from enum import Enum as PyEnum
from functools import wraps
import logging
import os
from urllib.parse import quote_plus

from authlib.integrations.flask_client import OAuth
from flask import abort
from flask_login import current_user, LoginManager
from flask_sqlalchemy import SQLAlchemy
from firebase_admin import credentials, initialize_app as initialize_firebase
from firebase_admin import firestore

from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, OUR_EMAILS

logging.basicConfig(
    filename='/home/model/apps/tournaments/app.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)

oauth = OAuth()
login_manager = LoginManager()
db = SQLAlchemy()

app_directory = os.path.dirname(os.path.realpath(__file__))
KEYFILE = os.path.join(app_directory, "fcm-admin.json")

initialize_firebase(credentials.Certificate(KEYFILE))
firestore_client = firestore.client()


class Role(PyEnum):
    admin = "admin"
    editor = "editor"
    scorer = "scorer"


def config_db(app):

    # Get the directory of the current file
    db_file = "tournaments.sqlite3"

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        app_directory, db_file
    )

    db.init_app(app)


def config_jinja(app):
    def prettyScore(score: int):
        if score < 0:
            prefix = "-"
        elif score > 0:
            prefix = "+"
        else:
            prefix = ""
        return f"{prefix}{(abs(round(score/10, 1)))}"

    def scoreClass(score: int):
        return "scorePos" if score > 0 else "scoreNeg" if score < 0 else "score0"

    def urlsafe(x):
        return quote_plus(x)

    env = app.jinja_env
    env.filters["prettyScore"] = prettyScore
    env.filters["scoreClass"] = scoreClass
    env.filters["urlsafe"] = urlsafe


def config_login_manager(app):
    login_manager.init_app(app)
    login_manager.login_view = "/login"


def config_oauth(app):
    oauth.init_app(app)
    oauth.register(
        "google",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        access_token_url="https://accounts.google.com/o/oauth2/token",
        access_token_params=None,
        authorize_url="https://accounts.google.com/o/oauth2/auth",
        authorize_params=None,
        api_base_url="https://www.googleapis.com/oauth2/v1/",
        client_kwargs={
            "scope": "email",
        },
    )

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return login_manager.unauthorized()
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.live_tournament_role != Role.admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def admin_or_editor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.live_tournament_role not in [Role.admin, Role.editor]:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def superadmin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.email not in OUR_EMAILS:
            abort(404)  # or 403 for Forbidden
        return f(*args, **kwargs)
    return decorated_function
