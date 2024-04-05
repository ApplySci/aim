# -*- coding: utf-8 -*-
"""
"""
import inspect
import os
import sys

from flask import Flask, render_template, send_from_directory

# add directory of this file, to the start of the path,
# before importing any of the app

sys.path.insert(
    0,
    os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(
        inspect.currentframe()))[0]))
    )

from create.tournament_setup import create_blueprint
from oauth_setup import config_oauth, config_login_manager

def create_app():
    app = Flask(__name__)
    app.register_blueprint(create_blueprint)
    app.config.from_object('config')
    app.debug = True
    config_oauth(app)
    config_login_manager(app)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(
            os.path.join(app.root_path, 'static'),
            'favicon.ico',
            mimetype='image/vnd.microsoft.icon',
            )

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
