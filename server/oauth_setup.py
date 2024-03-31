# -*- coding: utf-8 -*-

from authlib.integrations.flask_client import OAuth

oauth = OAuth()

def config_oauth(app):
    oauth.init_app(app)
    oauth.register(
        'google',
        client_id='your-client-id',
        client_secret='your-client-secret',
        access_token_url='https://accounts.google.com/o/oauth2/token',
        access_token_params=None,
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        authorize_params=None,
        api_base_url='https://www.googleapis.com/oauth2/v1/',
        client_kwargs={'scope': 'email',},
    )
