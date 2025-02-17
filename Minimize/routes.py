from flask import Flask, render_template, flash, redirect, url_for, session, request, Blueprint
print("Top of routes.py")
from Minimize import app, bcrypt, db
print("After app import in routes.py")
from Minimize.forms import RegistrationForm, LoginForm, IntroduceYourselfForm, YourHabitsForm
from Minimize.models import User, User_Socials, User_Habits
from flask_sqlalchemy import SQLAlchemy
from config import Config

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pgauser:hs@localhost:5432/minimize-db'
print(f"inside route app instance {id(app)}")
# db = SQLAlchemy(app)
@app.route('/')
def index():
    return render_template('welcome.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        session['first_name'] = form.first_name.data
        session['last_name'] = form.last_name.data
        session['email'] = form.email.data
        session['username'] = form.username.data
        session['password'] = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        flash("Sign-up successful! Now introduce yourself.", "success")
        return redirect(url_for('introduceyourself'))  # Proceed to the next form
    
    return render_template('signup.html', title='Sign Up', form=form)


@app.route('/introduceyourself', methods=['GET', 'POST'])
def introduceyourself():
    form = IntroduceYourselfForm()
    if form.validate_on_submit():
        session['instagram_handle'] = form.instagram_handle.data
        session['snapchat_handle'] = form.snapchat_handle.data
        session['profile_picture'] = form.profile_picture.data
        session['short_bio'] = form.short_bio.data

        flash("Socials saved! Now let's record your habits.", "success")
        return redirect(url_for('yourhabits'))  # Move to habits form
    
    return render_template('introduceyourself.html', title='Introduce Yourself', form=form)


@app.route('/yourhabits', methods=['GET', 'POST'])
def yourhabits():
    form = YourHabitsForm()
    if form.validate_on_submit():
        # Save habits data in session first
        session['sleep'] = form.sleep.data
        session['cleanliness'] = form.cleanliness.data
        session['relationship'] = form.relationship.data

        # Create and save User
        new_user = User(
            first_name=session.get('first_name'),
            last_name=session.get('last_name'),
            email=session.get('email'),
            username=session.get('username'),
            password_hash=session.get('password')
        )
        db.session.add(new_user)
        db.session.commit()  # User must be committed first to get an ID

        # Save User Socials
        new_socials = User_Socials(
            user_id=new_user.id,  # Link to User ID
            instagram_handle=session.get('instagram_handle'),
            snapchat_handle=session.get('snapchat_handle'),
            profile_picture=session.get('profile_picture'),
            short_bio=session.get('short_bio')
        )
        db.session.add(new_socials)

        # Save User Habits
        new_habits = User_Habits(
            user_id=new_user.id,  # Link to User ID
            sleep=session.get('sleep'),
            cleanliness=session.get('cleanliness'),
            relationship=session.get('relationship')
        )
        db.session.add(new_habits)

        db.session.commit()  # Commit everything at once

        # Clear session after saving
        session.clear()

        flash("Registration complete! You can now log in.", "success")
        return redirect(url_for('registrationcomplete'))
    
    return render_template('yourhabits.html', title='Your Habits', form=form)


@app.route('/registrationcomplete')
def registrationcomplete():
    return render_template('registrationcomplete.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('login.html', title='Login', form=form)

