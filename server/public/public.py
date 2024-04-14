# -*- coding: utf-8 -*-
'''
creates the tournament data pages for the public
'''
from flask import Blueprint, jsonify
from models import Hanchan, Tournament, User
from oauth_setup import db

public_blueprint = Blueprint('public', __name__)


@public_blueprint.route('/public/tournaments.json')
def index():
    """ We're not using this at present, and may never use it """
    full_list =  db.session.query(Tournament).with_entities(
        Tournament.title, Tournament.firebase_doc,
        ).all()
    tournaments = [{'title': t[0], 'doc': t[1],} for t in full_list]
    return jsonify(tournaments)
