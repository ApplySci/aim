# -*- coding: utf-8 -*-
"""
website root pages
"""

import os

from flask import Blueprint, current_app, render_template, send_from_directory

blueprint = Blueprint('root', __name__)

@blueprint.route('/')
def index():
    return render_template('index.html')

@blueprint.route('/privacy')
def privacy():
    return render_template('privacy.html')

@blueprint.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(current_app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon',
        )
