from flask import Flask, render_template, flash, redirect, url_for, session, request
# print("Top of routes.py")
from Minimize import app, bcrypt, db
import uuid
import os
# print("After app import in routes.py")
from Minimize.forms import RegistrationForm, LoginForm, IntroduceYourselfForm, YourHabitsForm, UpdateAccountForm, ItemForm
from Minimize.models import User, User_Socials, User_Habits, User_Items
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from config import Config


# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pgauser:hs@localhost:5432/minimize-db'
print(f"inside route app instance {id(app)}")

if not os.path.exists(app.config['PRO_PIC_UPLOAD_FOLDER']):
    os.makedirs(app.config['PRO_PIC_UPLOAD_FOLDER'])

if not os.path.exists(app.config['ITEM_UPLOAD_FOLDER']):
    os.makedirs(app.config['ITEM_UPLOAD_FOLDER'])
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
        session['short_bio'] = form.short_bio.data
        profile_picture = form.profile_picture.data
        if profile_picture:
            # Generate a unique filename with UUID
            file_extension = profile_picture.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"

            # Save the file to the upload folder
            file_path = os.path.join(app.config['PRO_PIC_UPLOAD_FOLDER'], unique_filename)
            profile_picture.save(file_path)

            # Store only the filename in session (NOT the file object)
            session['profile_picture'] = unique_filename
        else:
            session['profile_picture'] = 'default.jpeg'  # Default image if none is uploaded

        flash("Socials saved! Now let's record your habits.", "success")


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

        hashed_password = bcrypt.generate_password_hash(session.get('password')).decode('utf-8')

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

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        print(f"User: {user.username}")
        print(f"Password: {form.password
        .data}")
        print(f'Hash:{user.password_hash}')
        print(f'{bcrypt.check_password_hash(user.password_hash, form.password.data)}')
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash("You have been logged in!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Login Unsuccessful. Please check email and password", "danger")
    return render_template('signin.html', title='Sign In', form=form)

@app.route('/signout')
@login_required
def signout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Dashboard', user=current_user)

@app.route('/myprofile')
@login_required
def myprofile():
    user_socials = User_Socials.query.filter_by(user_id=current_user.id).first()
    user_habits = User_Habits.query.filter_by(user_id=current_user.id).first()
    return render_template('myprofile.html', title='Profile',user=current_user, user_socials=user_socials, user_habits=user_habits)

@app.route('/myprofile/update', methods=['GET', 'POST'])
@login_required
def updateprofile():
    user = current_user
    user_socials = User_Socials.query.filter_by(user_id=current_user.id).first()
    user_habits = User_Habits.query.filter_by(user_id=current_user.id).first()
    print(f"User Socials: {user_socials}")
    print(f"User Habits: {user_habits}")
    form_data = {
        "instagram_handle": user_socials.instagram_handle if user_socials else "",
        "snapchat_handle": user_socials.snapchat_handle if user_socials else "",
        "profile_picture": user_socials.profile_picture if user_socials else "",
        "short_bio": user_socials.short_bio if user_socials else "",
        "sleep": user_habits.sleep if user_habits else "",
        "cleanliness": user_habits.cleanliness if user_habits else "",
        "relationship": user_habits.relationship if user_habits else "",
    }
    print(f"Form Data: {form_data}")
    form = UpdateAccountForm(data=form_data)
    if form.validate_on_submit():
        print("Form Validated")
        # Update or Create Social Media Entry
        if user_socials:
            print("User Socials Exist and we are inside the if statement")
            user_socials.instagram_handle = form.instagram_handle.data
            user_socials.snapchat_handle = form.snapchat_handle.data
            user_socials.short_bio = form.short_bio.data
            profile_picture = form.profile_picture.data
            file_extension = profile_picture.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"

            file_path = os.path.join(app.config['PRO_PIC_UPLOAD_FOLDER'], unique_filename)
            profile_picture.save(file_path)
            user_socials.profile_picture = unique_filename

        print(f'User Socials: {user_socials}')
        if user_habits:
            user_habits.sleep = form.sleep.data
            user_habits.cleanliness = form.cleanliness.data
            user_habits.relationship = form.relationship.data
        print(f"User Habits: {user_habits}")
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profileupdated'))
    return render_template('updateprofile.html', title='Update Profile', form=form)

@app.route('/myitems')
@login_required
def myitems():
    return render_template('myitems.html', title='Items')

@app.route('/mygroups')
@login_required
def mygroups():
    return render_template('mygroups.html', title='Groups')

@app.route('/profileupdated')
@login_required
def profileupdated():
    return render_template('profileupdated.html', user=current_user)

@app.route('/myitems')
@login_required
def myitems():
    return render_template('myitems.html', title='Items', user=current_user)

@app.route('/add_item', methods=['GET', 'POST'])
@login_required
def add_item():
    form = ItemForm()

    if form.validate_on_submit():
        # Handle file upload
        if form.item_image.data:
            file_extension = form.item_image.data.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
            file_path = os.path.join(app.static_folder, 'item_images', unique_filename)
            form.item_image.data.save(file_path)
        else:
            unique_filename = 'default.jpeg'  # Default item image

        # Create new item record
        new_item = User_Items(
            user_id=current_user.id,
            item_name=form.item_name.data,
            item_image=unique_filename,
            description=form.description.data,
            is_sharable=form.is_sharable.data
        )

        db.session.add(new_item)
        db.session.commit()

        flash('Item added successfully!', 'success')
        return redirect(url_for('dashboard'))  # Change to your desired redirect page

    return render_template('add_item.html', form=form)