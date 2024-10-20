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
    os.path.realpath(
        os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0])
    ),
)

from accounts.accounts import blueprint as bp_accounts
from run.admin import blueprint as bp_admin
from create.tournament_setup import blueprint as bp_create
from root import blueprint as bp_root
from run.run import blueprint as bp_run
from run.cloud_edit import blueprint as bp_edit
from run.export import blueprint as bp_export
from oauth_setup import config_oauth, config_login_manager, config_db, config_jinja


def create_app():
    app = Flask(__name__)
    for bp in (bp_accounts, bp_create, bp_root, bp_run, bp_admin, bp_edit, bp_export):
        app.register_blueprint(bp)

    app.config.from_object("config")
    app.debug = True
    config_oauth(app)
    config_login_manager(app)
    config_db(app)
    config_jinja(app)
    return app


application = create_app()

if __name__ == "__main__":
    application.run(debug=True)
    pass
