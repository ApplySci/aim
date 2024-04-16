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

from accounts.accounts import blueprint as bp_accounts
from run.admin import blueprint as bp_admin
from create.tournament_setup import blueprint as bp_create
from public.public import blueprint as bp_public
from root import blueprint as bp_root
from run.run import blueprint as bp_run
from oauth_setup import config_oauth, config_login_manager, config_db

def create_app():
    app = Flask(__name__)
    for bp in (bp_accounts, bp_create, bp_public, bp_root, bp_run, bp_admin):
        app.register_blueprint(bp)

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
