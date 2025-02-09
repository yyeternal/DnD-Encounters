from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, FloatField, DecimalField, SelectField
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from wtforms.validators import  ValidationError, DataRequired, EqualTo, Email, Length, NumberRange, AnyOf
from wtforms.widgets import ListWidget, CheckboxInput
from app.main.models import User 
from flask import redirect
from app import db
import sqlalchemy as sqla
import re

def is_unique(field_name):
    if field_name == 'username':
        def _is_unique_username(form, field):
            user = db.session.scalars(sqla.select(User).where(User.username == field.data)).first()
            if user is not None:
                # return redirect('auth.login')
                raise ValidationError(message="There is already an account with that username")
        return _is_unique_username
    elif field_name == 'id':
        def _is_unique_id(form, field):
            user = db.session.scalars(sqla.select(User).where(User.id == field.data)).first()
            if user is not None:
                # return redirect('auth.login')
                raise ValidationError(message="There is already an account with that ID")
        return _is_unique_id 

class LoginForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired()])
    password = PasswordField('Password', validators = [DataRequired()])
    remember_me = BooleanField('Remember me?')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired('Error, must enter a value'), is_unique('username')])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')