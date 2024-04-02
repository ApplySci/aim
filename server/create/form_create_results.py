# -*- coding: utf-8 -*-
"""
@author: ZAPS@mahjong.ie
"""
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, NumberRange, Optional


class GameParametersForm(FlaskForm):
    table_count = IntegerField(
        'Number of tables [1-20] (players divided by 4)',
        default = 10,
        validators=[DataRequired(), NumberRange(min=1, max=20)])
    game_count = IntegerField(
        'Number of hanchan [1-20]',
        default = 7,
        validators=[DataRequired(), NumberRange(min=1, max=20)])
    title = StringField('Spreadsheet Title',
                        default = 'Riichi Tournament Scoresheet',
                        validators=[DataRequired()],
                        )
    notify = BooleanField(
        'Notify the scorer as soon as the scoresheet has been created',
        default = True,
        )
    emails = StringField("Scorer's email address", validators=[
        Optional(),
        Email(),
        ])
    submit = SubmitField('Create the google sheet')
