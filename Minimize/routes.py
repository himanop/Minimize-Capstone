from flask import Flask, render_template, flash, redirect, url_for, session, request, jsonify, current_app
from itsdangerous import URLSafeTimedSerializer
from werkzeug.utils import secure_filename
# print("Top of routes.py")
from Minimize import app, bcrypt, db
import uuid
import os
from Minimize.send_email import send_verification_email, send_reset_email
from Minimize.forms import RequestResetForm, ResetPasswordForm
from Minimize.utils import confirm_token, confirm_reset_token, generate_confirmation_token, generate_reset_token
# print("After app import in routes.py")
from Minimize.forms import RegistrationForm, LoginForm, IntroduceYourselfForm, YourHabitsForm, UpdateAccountForm, ItemForm, CreateGroupForm
from Minimize.models import User, User_Socials, User_Habits, User_Items, Group, group_membership, Message
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from config import Config

print(f"inside route app instance {id(app)}")

if not os.path.exists(app.config['PRO_PIC_UPLOAD_FOLDER']):
    os.makedirs(app.config['PRO_PIC_UPLOAD_FOLDER'])

if not os.path.exists(app.config['ITEM_UPLOAD_FOLDER']):
    os.makedirs(app.config['ITEM_UPLOAD_FOLDER'])

if not os.path.exists(app.config['GROUP_PIC_UPLOAD_FOLDER']):
    os.makedirs(app.config['GROUP_PIC_UPLOAD_FOLDER'])

def allowed_file(filename):
    """Check if a file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'gif'}

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

@app.route('/resend_verification', methods=['GET', 'POST'])
def resend_verification():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            if user.is_verified:
                flash('Account already verified. Please sign in.', 'info')
                return redirect(url_for('signin'))
            send_verification_email(user)
            flash('Verification email has been resent. Check your inbox.', 'success')
        else:
            flash('Email not found. Please register.', 'danger')
        return redirect(url_for('resend_verification'))

    return render_template('resend_verification.html')


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

        # hashed_password = bcrypt.generate_password_hash(session.get('password')).decode('utf-8')

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

        send_verification_email(new_user)
        flash("Registration complete! Check your email to verify your account.", "info")
        return redirect(url_for('signin'))  # Redirect to login page
    
    return render_template('yourhabits.html', title='Your Habits', form=form)


@app.route('/registrationcomplete')
def registrationcomplete():
    return render_template('registrationcomplete.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            if not user.is_verified:
                flash("Please verify your email before logging in.", "warning")
                return redirect(url_for('signin'))
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

    form_data = {
        "instagram_handle": user_socials.instagram_handle if user_socials else "",
        "snapchat_handle": user_socials.snapchat_handle if user_socials else "",
        "profile_picture": user_socials.profile_picture if user_socials else "",
        "short_bio": user_socials.short_bio if user_socials else "",
        "sleep": user_habits.sleep if user_habits else "",
        "cleanliness": user_habits.cleanliness if user_habits else "",
        "relationship": user_habits.relationship if user_habits else "",
    }
    form = UpdateAccountForm(data=form_data)

    if form.validate_on_submit():
        print("Form Validated")

        # Update or create User_Socials
        if user_socials:
            print("User Socials Exist and we are inside the if statement")
            user_socials.instagram_handle = form.instagram_handle.data
            user_socials.snapchat_handle = form.snapchat_handle.data
            user_socials.short_bio = form.short_bio.data

            if form.profile_picture.data:
                profile_picture = form.profile_picture.data
                if hasattr(profile_picture, 'filename') and profile_picture.filename:
                    file_extension = profile_picture.filename.rsplit('.', 1)[1].lower()
                    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"

                    file_path = os.path.join(app.config['PRO_PIC_UPLOAD_FOLDER'], unique_filename)
                    profile_picture.save(file_path)
                    user_socials.profile_picture = unique_filename

        print(f'User Socials: {user_socials}')

        # Update or create User_Habits
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


from sqlalchemy import or_

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    search_results = None

    if request.method == 'POST':
        search_query = request.form.get('username', '').strip()

        if search_query:
            search_results = User.query.filter(
                or_(
                    User.username.ilike(f"%{search_query}%"),
                    User.first_name.ilike(f"%{search_query}%"),
                    User.last_name.ilike(f"%{search_query}%")
                )
            ).all()

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

        # Handle image update correctly
        if form.item_image.data and hasattr(form.item_image.data, 'filename'):  # Check if a new file was uploaded
            file_extension = form.item_image.data.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
            file_path = os.path.join(app.static_folder, 'item_pics', unique_filename)
            form.item_image.data.save(file_path)
            item.item_image = unique_filename  # Update with new image filename

        db.session.commit()
        flash('Item updated successfully!', 'success')
        return redirect(url_for('myitems'))

    return render_template('updateitem.html', form=form, item=item)


@app.route('/mygroups')
@login_required
def mygroups():
    # Fetch groups created by the current user through query
    # If current user.id is the creator_id of the group then store the group in the created_groups list
    created_groups = Group.query.filter_by(creator_id=current_user.id).all()
    print(f"Here are the users created Groups: {created_groups}")

    # Fetch groups the current user is a member of but did not create
    # current_user.groups is a list of all groups the user is a member of
    # here we are looping through the groups that the current user is in and only adding the groups that the current user did not create
    # to the member_groups list
    # We are adding the entire group object to the member_groups list(ex. Group(id=2, creator_id=12)).
    # The first "group" stores the variable/object that we are adding to the list.
    # Once we have the group object we can access the group's attributes like group.id, group.creator_id, group.description, etc.
    member_groups = [group for group in current_user.groups if group.creator_id != current_user.id]
    print(f"Here are the users member Groups: {member_groups}")

    return render_template('mygroups.html', created_groups=created_groups, member_groups=member_groups)

@app.route('/creategroup', methods=['GET', 'POST'])
@login_required
def creategroup():
    form = CreateGroupForm()

    if request.method == 'POST':
        if form.submit.data:
            group_name = form.group_name.data
            address = form.address.data
            member_ids = request.form.get('members', '').split(',')
            member_ids = [int(id) for id in member_ids if id.strip()]
            profile_picture = form.profile_picture.data

            # Check if the group name already exists
            existing_group = Group.query.filter_by(group_name=group_name).first()
            if existing_group:
                flash('Group name already exists!', 'error')
                return redirect(url_for('creategroup'))

            # Handle profile picture upload
            profile_picture_filename = 'default_group.jpg'
            if profile_picture and allowed_file(profile_picture.filename):
                filename = secure_filename(profile_picture.filename)
                file_path = os.path.join(app.config['GROUP_PIC_UPLOAD_FOLDER'], filename)
                profile_picture.save(file_path)
                profile_picture_filename = filename

            # Create a new group
            new_group = Group(
                group_name=group_name,
                address=address,
                profile_picture=profile_picture_filename,
                creator_id=current_user.id
            )
            db.session.add(new_group)
            db.session.commit()

            # Add the current user as the first member
            new_group.members.append(current_user)

            # Add selected users to the group (avoid duplicates)
            for user_id in member_ids:
                try:
                    user_id = int(user_id)
                    user = User.query.get(user_id)
                    if user and user not in new_group.members:
                        new_group.members.append(user)
                except (ValueError, TypeError):
                    flash(f"Invalid user ID: {user_id}", "error")

            db.session.commit()
            flash('Group created successfully!', 'success')
            return redirect(url_for('view_group', group_id=new_group.id))

    return render_template('creategroup.html', form=form)


@app.route('/search_users')
@login_required
def search_users():
    #Below we are getting the query from the search bar from the fetch function in our JS code
    search_query = request.args.get('query', '').strip()
    if search_query:
        # Search for users by username, first name, or last name
        users = User.query.filter(
            (User.username.ilike(f'%{search_query}%')) |
            (User.first_name.ilike(f'%{search_query}%')) |
            (User.last_name.ilike(f'%{search_query}%'))
        ).all()
        users_data = [{'id': user.id, 'username': user.username, 'first_name': user.first_name, 'last_name': user.last_name} for user in users]
        return jsonify(users_data)
    return jsonify([])


@app.route('/group/<int:group_id>', methods=['GET', 'POST'])
@login_required
# Route below allows users to view a group they are in
# If they are the owner they have the ability to add and remove members
def view_group(group_id):
    group = Group.query.get_or_404(group_id)

    # Ensure the current user is a member of the group
    if current_user not in group.members:
        flash("You are not a member of this group.", "error")
        return redirect(url_for('mygroups'))

    # Check if the current user is the group owner
    is_owner = group.creator_id == current_user.id

    # Handle adding a new member
    if request.method == 'POST' and is_owner:
        if 'add_member' in request.form:
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
                flash("User not found.", "error")

        elif 'edit_group' in request.form:
            new_group_name = request.form.get('group_name')
            new_address = request.form.get('address')
            new_profile_picture = request.files.get('profile_picture')

            group.group_name = new_group_name
            group.address = new_address

            if new_profile_picture and new_profile_picture.filename != '':
                filename = secure_filename(new_profile_picture.filename)
                pic_path = os.path.join(app.root_path, 'static', 'group_pics', filename)
                new_profile_picture.save(pic_path)
                group.profile_picture = filename

            db.session.commit()
            flash("Group details updated successfully.", "success")


        # Handle removing a member
        elif 'remove_member' in request.form:
            # Below we get the member/user id to remove user from the group
            user_id = request.form.get('user_id')

            user_to_remove = User.query.get(user_id)

            if user_to_remove and user_to_remove in group.members:
                group.members.remove(user_to_remove)
                db.session.commit()
                flash(f"{user_to_remove.username} has been removed from the group.", "success")
            else:
                flash("User not found in the group.", "error")

        elif 'delete_group' in request.form:
            db.session.delete(group)
            db.session.commit()
            flash("Group has been deleted.", "success")
            return redirect(url_for('mygroups'))

    return render_template('viewgroup.html', group=group, is_owner=is_owner)

# Render chat page
@app.route('/group/<int:group_id>/chat')
@login_required
def group_chat(group_id):
    group = Group.query.get_or_404(group_id)
    if current_user not in group.members:
        flash("You are not a member of this group.", "danger")
        return redirect(url_for('mygroups'))
    return render_template('groupchat.html', group=group)


# Return messages as JSON
@app.route('/group/<int:group_id>/chat/messages')
@login_required
def get_messages(group_id):
    messages = Message.query.filter_by(group_id=group_id).order_by(Message.timestamp).all()
    return jsonify([
        {
            'username': m.user.username,
            'content': m.content,
            'timestamp': m.timestamp.strftime('%H:%M')
        } for m in messages
    ])


# Handle message submission
@app.route('/group/<int:group_id>/chat/send', methods=['POST'])
@login_required
def send_message(group_id):
    content = request.json.get('message')
    if content:
        msg = Message(content=content, user_id=current_user.id, group_id=group_id)
        db.session.add(msg)
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 400

@app.route('/confirm/<token>')
def confirm_email(token):
    email = confirm_token(token)
    if not email:
        flash("The confirmation link is invalid or has expired.", "danger")
        return redirect(url_for('signin'))

    user = User.query.filter_by(email=email).first_or_404()
    if user.is_verified:
        flash("Account already verified. Please log in.", "info")
    else:
        user.is_verified = True
        db.session.commit()
        flash("Your account has been verified. You can now log in.", "success")

    return redirect(url_for('signin'))

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
            flash('Check your email for a password reset link.', 'info')
        else:
            flash('No account with that email exists.', 'danger')
        return redirect(url_for('signin'))
    return render_template('reset_request.html', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    email = confirm_reset_token(token)
    if not email:
        flash('The reset link is invalid or expired.', 'warning')
        return redirect(url_for('reset_request'))
    
    user = User.query.filter_by(email=email).first_or_404()
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password_hash = hashed_pw
        db.session.commit()
        flash('Your password has been updated. You can now log in.', 'success')
        return redirect(url_for('signin'))
    return render_template('reset_token.html', form=form)

# @app.route('/group/<int:group_id>/chat', methods=['GET', 'POST'])
# @login_required
# def group_chat(group_id):
#     group = Group.query.get_or_404(group_id)

#     # Ensure the current user is a member of the group
#     if current_user not in group.members:
#         flash("You are not a member of this group.", "error")
#         return redirect(url_for('mygroups'))

#     # Handle sending a new message
#     if request.method == 'POST':
#         content = request.form.get('content')
#         if content:
#             new_message = Message(
#                 content=content,
#                 user_id=current_user.id,
#                 group_id=group.id
#             )
#             db.session.add(new_message)
#             db.session.commit()

#     # Retrieve all messages for the group
#     messages = Message.query.filter_by(group_id=group.id).order_by(Message.timestamp.asc()).all()

#     return render_template('group_chat.html', group=group, messages=messages)

# @app.route('/leave_group/<int:group_id>', methods=['POST'])
# @login_required
# def leave_group(group_id):
#     group = Group.query.get_or_404(group_id)

#     # Ensure the user is in the group
#     if current_user in group.members:
#         group.members.remove(current_user)
#         db.session.commit()
#         flash(f'You have left the group "{group.group_name}".', 'success')
#     else:
#         flash('You are not a member of this group.', 'danger')

#     return redirect(url_for('mygroups'))

# @app.route('/delete_group/<int:group_id>', methods=['GET', 'POST'])
# @login_required
# def delete_group(group_id):
#     group = Group.query.get_or_404(group_id)

#     # Ensure only the creator (first member) can delete the group
#     if current_user != group.members[0]:
#         flash("You are not authorized to delete this group.", "danger")
#         return redirect(url_for('view_group', group_id=group.id))

#     if request.method == 'POST':
#         db.session.delete(group)
#         db.session.commit()
#         flash(f'Group "{group.group_name}" has been deleted.', 'success')
#         return redirect(url_for('mygroups'))

#     return render_template('deletegroup.html', group=group)

# @app.route('/add_member/<int:group_id>', methods=['POST'])
# @login_required
# def add_member(group_id):
#     group = Group.query.get_or_404(group_id)

#     # Ensure only the group creator can add members
#     if current_user != group.members[0]:
#         flash("You are not authorized to add members to this group.", "danger")
#         return redirect(url_for('view_group', group_id=group.id))

#     username = request.form.get('username').strip()
#     user_to_add = User.query.filter_by(username=username).first()

#     if user_to_add:
#         if user_to_add in group.members:
#             flash(f"{username} is already in the group.", "warning")
#         else:
#             group.members.append(user_to_add)
#             db.session.commit()
#             flash(f"{username} has been added to the group!", "success")
#     else:
#         flash("User not found.", "danger")

#     return redirect(url_for('view_group', group_id=group.id))
