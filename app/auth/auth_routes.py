
from flask import render_template, flash, redirect, url_for, session, request

import os
from app import db
from app.auth import auth_blueprint as bp_auth 
import sqlalchemy as sqla

from app.main.models import User
from app.auth.auth_forms import LoginForm, RegistrationForm

from flask_login import login_user, current_user, logout_user, login_required
from config import Config
import identity.web

authent = identity.web.Auth(
        session=session,
        authority=os.getenv("AUTHORITY"),
        client_id=os.getenv("CLIENT_ID"),
        client_credential=os.getenv("CLIENT_SECRET"),
    )

@bp_auth.route('/user/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    lform = LoginForm()
    if lform.validate_on_submit():
        query = sqla.select(User).where(User.username == lform.username.data)
        user = db.session.scalars(query).first()
        if (user is None) or (user.check_password(lform.password.data) == False):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember = lform.remember_me.data)
        flash('The user {} has succesfully logged in! '.format(current_user.username))

        return redirect(url_for('main.index'))
    return render_template('login.html', form = lform)

@bp_auth.route('/user/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp_auth.route('register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    sform = RegistrationForm()
    if sform.validate_on_submit():
        user = User( username = sform.username.data)  
        user.set_password(sform.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form = sform)    

