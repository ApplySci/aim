# -*- coding: utf-8 -*-
"""
"""
import inspect
import os
import sys

from flask import Flask

# add directory of this file, to the start of the path,
# before importing any of the app
sys.path.insert(
    0,
    os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(
        inspect.currentframe()))[0]))
    )

from create.tournament_setup import create_blueprint
from public.public import public_blueprint
from root import root_blueprint
from oauth_setup import config_oauth, config_login_manager, config_db

def create_app():
    app = Flask(__name__)
    app.register_blueprint(create_blueprint)
    app.register_blueprint(public_blueprint)
    app.register_blueprint(root_blueprint)
    app.config.from_object('config')
    app.debug = True
    config_oauth(app)
    config_login_manager(app)
    config_db(app)
    return app

application = create_app()

@application.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


if __name__ == '__main__':
    application.run(debug=True)
    pass
