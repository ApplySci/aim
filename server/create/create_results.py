# -*- coding: utf-8 -*-
"""
Created on Sun Mar 31 08:04:41 2024

@author: ZAPS@mahjong.ie
"""
from flask_wtf import FlaskForm
from wtforms import FieldList, StringField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, NumberRange

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
        'Notify scorers of the scoresheet URL, as soon as the scoresheet has been created?',
        default = True,
        )
    emails = FieldList(StringField(
        '',
        validators=[Email()],
        ), min_entries=5,
        )
    submit = SubmitField('Create the google sheet')
