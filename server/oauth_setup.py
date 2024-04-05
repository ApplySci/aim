# -*- coding: utf-8 -*-

from authlib.integrations.flask_client import OAuth
from flask_login import LoginManager
from flask_socketio import SocketIO

from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

oauth = OAuth()
login_manager = LoginManager()

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
