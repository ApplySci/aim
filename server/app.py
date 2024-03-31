# -*- coding: utf-8 -*-
"""
"""
import os

from flask import Flask, render_template, send_from_directory

from create.tournament_setup import create_blueprint
from oauth_setup import config_oauth

def create_app():
    app = Flask(__name__)
    app.register_blueprint(create_blueprint)
    app.config.from_object('config')
    app.debug = True
    config_oauth(app)

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

if __name__ == '__main__':
    create_app().run(debug=True)
