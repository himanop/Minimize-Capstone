from flask import Flask, render_template, flash, redirect, url_for, session, request
# print("Top of routes.py")
from Minimize import app, bcrypt, db
import uuid
import os
# print("After app import in routes.py")
from Minimize.forms import RegistrationForm, LoginForm, IntroduceYourselfForm, YourHabitsForm, UpdateAccountForm, ItemForm, CreateGroupForm
from Minimize.models import User, User_Socials, User_Habits, User_Items, Group
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from config import Config


# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pgauser:hs@localhost:5432/minimize-db'
print(f"inside route app instance {id(app)}")

if not os.path.exists(app.config['PRO_PIC_UPLOAD_FOLDER']):
    os.makedirs(app.config['PRO_PIC_UPLOAD_FOLDER'])

if not os.path.exists(app.config['ITEM_UPLOAD_FOLDER']):
    os.makedirs(app.config['ITEM_UPLOAD_FOLDER'])

if not os.path.exists(app.config['GROUP_PIC_UPLOAD_FOLDER']):
    os.makedirs(app.config['GROUP_PIC_UPLOAD_FOLDER'])
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

@app.route('/profileupdated')
@login_required
def profileupdated():
    return render_template('profileupdated.html', user=current_user)

@app.route('/myitems')
@login_required
def myitems():
    page = request.args.get('page', 1, type=int)  # Get the current page number, default is 1
    per_page = 5  # Number of items per page
    user_id = request.args.get('user_id', type=int)  # Get user_id from query params

    # Determine which user's items to show
    if user_id:
        user = User.query.get_or_404(user_id)  # Fetch the specified user
    else:
        user = current_user  # Default to the logged-in user

    # Fetch paginated items for the selected user
    paginated_items = User_Items.query.filter_by(user_id=user.id).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('myitems.html', title=f"{user.first_name}'s Items", user=user, paginated_items=paginated_items)


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    search_results = None  # Default to None if no search is performed

    if request.method == 'POST':
        search_query = request.form.get('username', '').strip()  # Get input and remove extra spaces

        if search_query:
            search_results = User.query.filter(User.username.ilike(f"%{search_query}%")).all()  # Case-insensitive search

    return render_template('search.html', search_results=search_results)

@app.route('/user/<int:user_id>')
@login_required
def view_user(user_id):
    user = User.query.get_or_404(user_id)  # Fetch user or return 404
    user_socials = User_Socials.query.filter_by(user_id=user_id).first()
    user_habits = User_Habits.query.filter_by(user_id=user_id).first()
    return render_template('view_user.html', user=user, user_socials=user_socials, user_habits=user_habits)


@app.route('/myitems/add_item', methods=['GET', 'POST'])
@login_required
def add_item():
    form = ItemForm()

    if form.validate_on_submit():
        # Handle file upload
        if form.item_image.data:
            file_extension = form.item_image.data.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
            file_path = os.path.join(app.static_folder, 'item_pics', unique_filename)
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
        return redirect(url_for('myitems'))  # Change to your desired redirect page

    return render_template('additem.html', form=form)

@app.route('/myitems/update/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    item = User_Items.query.get_or_404(item_id)

    # Ensure only the item owner can edit it
    if item.user_id != current_user.id:
        flash("You don't have permission to update this item.", "danger")
        return redirect(url_for('myitems'))

    form = ItemForm(obj=item)

    if form.validate_on_submit():
        item.item_name = form.item_name.data
        item.description = form.description.data
        item.is_sharable = form.is_sharable.data

        # Handle image update
        if form.item_image.data:
            file_extension = form.item_image.data.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
            file_path = os.path.join(app.static_folder, 'item_pics', unique_filename)
            form.item_image.data.save(file_path)
            item.item_image = unique_filename  # Update the image filename

        db.session.commit()
        flash('Item updated successfully!', 'success')
        return redirect(url_for('myitems'))

    return render_template('updateitem.html', form=form, item=item)

@app.route('/mygroups', methods=['GET', 'POST'])
@login_required
def mygroups():
    return render_template('mygroups.html', title='Groups', user=current_user)

@app.route('/creategroup', methods=['GET', 'POST'])
@login_required
def creategroup():
    form = CreateGroupForm()

    # Ensure choices are always set before rendering the form
    form.members.choices = []  # Default empty choices to prevent "NoneType" error

    selected_users = []  # Store selected members between searches

    # Preserve previously selected members from form submission
    selected_user_ids = request.form.getlist('selected_users')
    if selected_user_ids:
        selected_users = User.query.filter(User.id.in_(selected_user_ids)).all()

    # If searching for users
    if 'submit_search' in request.form:
        search_query = form.search_username.data.strip()

        # Perform new search
        if search_query:
            found_users = User.query.filter(User.username.ilike(f"%{search_query}%")).all()
        else:
            found_users = []

        # Merge previous selections and new search results
        all_users = {user.id: f"{user.first_name} {user.last_name} (@{user.username})" for user in selected_users + found_users}
        form.members.choices = list(all_users.items())

    # If adding a user to the selection
    elif 'add_user' in request.form:
        new_user_id = request.form.get('new_user_id')
        if new_user_id and new_user_id not in selected_user_ids:
            selected_user_ids.append(new_user_id)
            selected_users = User.query.filter(User.id.in_(selected_user_ids)).all()

    # If creating the group
    elif form.validate_on_submit() and 'submit' in request.form:
        # Handle profile picture upload
        if form.profile_picture.data:
            file_extension = form.profile_picture.data.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
            file_path = os.path.join(app.config['PRO_PIC_UPLOAD_FOLDER'], unique_filename)
            form.profile_picture.data.save(file_path)
        else:
            unique_filename = 'default_group.jpg'  # Default group image

        # Create the new group
        new_group = Group(
            group_name=form.group_name.data,
            profile_picture=unique_filename,
            address=form.address.data
        )
        new_group.members.append(current_user)  # Add the creator to the group

        # Add selected users
        for user_id in selected_user_ids:
            user = User.query.get(user_id)
            if user:
                new_group.members.append(user)

        db.session.add(new_group)
        db.session.commit()

        flash(f'Group "{form.group_name.data}" created successfully!', 'success')
        return redirect(url_for('view_group', group_id=new_group.id))

    return render_template('creategroup.html', form=form, selected_users=selected_users)


@app.route('/group/<int:group_id>')
@login_required
def view_group(group_id):
    group = Group.query.get_or_404(group_id)

    # Check if the current user is a member of the group
    if current_user not in group.members:
        flash("You are not a member of this group.", "danger")
        return redirect(url_for('mygroups'))

    return render_template('viewgroup.html', group=group)

@app.route('/leave_group/<int:group_id>', methods=['POST'])
@login_required
def leave_group(group_id):
    group = Group.query.get_or_404(group_id)

    # Ensure the user is in the group
    if current_user in group.members:
        group.members.remove(current_user)
        db.session.commit()
        flash(f'You have left the group "{group.group_name}".', 'success')
    else:
        flash('You are not a member of this group.', 'danger')

    return redirect(url_for('mygroups'))

@app.route('/delete_group/<int:group_id>', methods=['GET', 'POST'])
@login_required
def delete_group(group_id):
    group = Group.query.get_or_404(group_id)

    # Ensure only the creator (first member) can delete the group
    if current_user != group.members[0]:
        flash("You are not authorized to delete this group.", "danger")
        return redirect(url_for('view_group', group_id=group.id))

    if request.method == 'POST':
        db.session.delete(group)
        db.session.commit()
        flash(f'Group "{group.group_name}" has been deleted.', 'success')
        return redirect(url_for('mygroups'))

    return render_template('deletegroup.html', group=group)

@app.route('/add_member/<int:group_id>', methods=['POST'])
@login_required
def add_member(group_id):
    group = Group.query.get_or_404(group_id)

    # Ensure only the group creator can add members
    if current_user != group.members[0]:
        flash("You are not authorized to add members to this group.", "danger")
        return redirect(url_for('view_group', group_id=group.id))

    username = request.form.get('username').strip()
    user_to_add = User.query.filter_by(username=username).first()

    if user_to_add:
        if user_to_add in group.members:
            flash(f"{username} is already in the group.", "warning")
        else:
            group.members.append(user_to_add)
            db.session.commit()
            flash(f"{username} has been added to the group!", "success")
    else:
        flash("User not found.", "danger")

    return redirect(url_for('view_group', group_id=group.id))
