from flask import Flask, render_template, flash, redirect, url_for, session
from Minimize import app, bcrypt
from Minimize.forms import RegistrationForm, LoginForm, IntroduceYourselfForm, YourHabitsForm
# from app import app

@app.route('/')
def index():
    return render_template('welcome.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        username = form.username.data
        return redirect(url_for('signup'))
    return render_template('signup.html', title='Sign Up', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('login.html', title='Login', form=form)

@app.route('/introduceyourself', methods=['GET', 'POST'])
def introduceyourself():
    form = IntroduceYourselfForm()
    return render_template('introduceyourself.html', title='Introduce Yourself', form=form)

@app.route('/yourhabits', methods=['GET', 'POST'])
def yourhabits():
    form = YourHabitsForm()
    return render_template('yourhabits.html', title='Your Habits', form=form)

