# -*- coding: utf-8 -*-
"""
"""
import inspect
import os
import sys

from flask import Flask, make_response, request, render_template

# add directory of this file, to the start of the path,
# before importing any of the app
sys.path.insert(
    0,
    os.path.realpath(
        os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0])
    ),
)

from accounts.accounts import blueprint as bp_accounts
from create.tournament_setup import blueprint as bp_create
from oauth_setup import config_oauth, config_login_manager, config_db, config_jinja
from run.admin import blueprint as bp_admin
from root import blueprint as bp_root
from run.run import blueprint as bp_run
from run.cloud_edit import blueprint as bp_edit
from run.export import blueprint as bp_export
from run.user_management import blueprint as bp_user_management
from config import SUPERADMIN


def create_app():
    app = Flask(__name__)
    for bp in (
        bp_accounts,
        bp_create,
        bp_root,
        bp_run,
        bp_admin,
        bp_edit,
        bp_export,
        bp_user_management,
    ):
        app.register_blueprint(bp)

    app.config.from_object("config")
    app.debug = True
    config_oauth(app)
    config_login_manager(app)
    config_db(app)
    config_jinja(app)

    @app.context_processor
    def inject_superadmin():
        return dict(SUPERADMIN=SUPERADMIN)

    @app.errorhandler(Exception)
    def handle_exception(e):
        import traceback
        tb = traceback.format_exc()
        return render_template(
            'error.html',
            error=str(e),
            traceback=tb
        ), 500

    @app.after_request
    def add_header(response):
        if request.path.startswith("/static/"):
            return response

        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "-1"
        return response

    return app


application = create_app()

if __name__ == "__main__":
    application.run(debug=True)
    pass
