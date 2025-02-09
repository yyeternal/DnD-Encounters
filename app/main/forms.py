from flask_wtf import FlaskForm
from app import db
import sqlalchemy as sqla

from app.main.models import MonsterGroup, PlayerGroup, Combat
from wtforms import StringField, SubmitField, PasswordField, IntegerField, FloatField, FormField, FieldList, SelectField, SelectMultipleField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, NumberRange
from wtforms.widgets import ListWidget, CheckboxInput

class CreateMonsterForm(FlaskForm):
    challenge_rating = SelectField('CR',
                        choices=[(.125, '0.125'), (.25, '0.25'), (.5, '0.5'), (1, '1'),
                                 (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7'),
                                 (8, '8'), (9, '9'), (10, '10'), (11, '11'), (12, '12'), 
                                 (13, '13'), (14, '14'), (15, '15'), (16, '16'), (17, '17'), 
                                 (18, '18'), (19, '19'), (20, '20'), (21, '21'), (22, '22'),
                                 (23, '23'), (24, '24'), (25, '25'), (26, '26'), (27, '27'), 
                                 (28, '28'), (29, '29'), (30, '30')],
                        coerce=float)
    quantity = IntegerField('Number of Monsters', validators=[DataRequired(), NumberRange(min=1)])

class CreateMonsterGroupsForm(FlaskForm):
    monster_groups = FieldList(FormField(CreateMonsterForm), min_entries=1)
    submit = SubmitField('Create Monster Groups')

class CreatePlayerForm(FlaskForm):
    level = IntegerField('Level', validators=[DataRequired(), NumberRange(min=1, max=20)])
    quantity = IntegerField('Number of Players', validators=[DataRequired(), NumberRange(min=1)])

class CreatePlayerGroupsForm(FlaskForm):
    player_groups = FieldList(FormField(CreatePlayerForm), min_entries=1)
    submit = SubmitField('Create Player Groups')

class CreateCombatForm(FlaskForm):
    player = SelectMultipleField('Select Players', choices=[], coerce=str)
    monster = SelectMultipleField('Select Monsters', choices=[], coerce=str)
    submit = SubmitField('Create Combat')

    def __init__(self, user_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user_id:
            self.player.choices = [
                (str(pg.id), f"Level {pg.level} - Qty {pg.quantity}") 
                for pg in PlayerGroup.query.filter_by(user_id=user_id).all()
            ]
            self.monster.choices = [
                (str(mg.id), f"CR {mg.challenge_rating} - Qty {mg.quantity}") 
                for mg in MonsterGroup.query.filter_by(user_id=user_id).all()
            ]

class DeleteCombatForm(FlaskForm):
    submit = SubmitField("Delete")