# -*- coding: utf-8 -*-
"""
@author: ZAPS@mahjong.ie
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class PickTournament(FlaskForm):
    sheet_id = StringField(
        'The long document id of your google scoresheet',
        validators=[DataRequired(),])
    submit = SubmitField('Go get it, tiger')
