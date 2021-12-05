import re
import flask_login

from flask_login.utils import login_required
from flask_migrate import current
from werkzeug.utils import redirect
from wtforms.validators import Email
from app import app, db
from app.forms import RegistrationForm

from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse

from app.forms import LoginForm, EditProfileForm
from flask_login import current_user, login_user, logout_user
from app.models import User

from datetime import datetime


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {"username": "Prasant Mahato"}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template("index.html", title = "Home Page", posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        # flash('Login requested for user {}, remember_me={}'.format(form.username.data, form.remember_me.data))

        #Check for the user in the database
        user = User.query.filter_by(username=form.username.data).first()
        
        # When a wrong user or password is entered
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        
        # Now as the login is successful, current_user is set to user
        login_user(user, remember=form.remember_me.data)

        # Redirect to previous page after login_required validation
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != ' ':
            next_page = url_for('index')

        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


# Method to logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Method to register users 
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Insert registered user to database
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

# User profile view function
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author' : user, 'body' : 'Test Post #1'},
        {'author' : user, 'body' : 'Test Post #2'}
    ]
    return render_template('user.html', title = username, user=user, posts=posts)

# Recording the last visit time for a user
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

# Edit profile view function
@app.route('/edit_profile', methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    
    return render_template('edit_profile.html', title='Edit Profile', form=form)

