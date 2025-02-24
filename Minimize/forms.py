from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, URLField, BooleanField, EmailField, FileField, DateField, SubmitField, SelectField
from flask_wtf.file import FileAllowed, FileRequired, FileField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from Minimize.models import User, User_Socials, User_Habits

class RegistrationForm(FlaskForm):
    #The variable names are how we are going to refer to the fields in the HTML code
    first_name = StringField('First Name', validators=[DataRequired()], render_kw={"placeholder": "First Name"})
    last_name = StringField('Last Name', validators=[DataRequired()], render_kw={"placeholder": "Last Name"})
    #This is just a comment
    email = EmailField('Email', validators=[DataRequired()], render_kw={"placeholder": "Email"})
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=4, max=15)],render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[DataRequired()],render_kw={"placeholder": "Password"})
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')], render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField('Create Account')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username taken! Please choose different username or sign in.')
        
    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('Email taken! Please choose different email or login.')

class IntroduceYourselfForm(FlaskForm):
    instagram_handle = StringField('Instagram Handle', render_kw={"placeholder": "Leave empty if you don't have one"})
    snapchat_handle = StringField('Snapchat Handle', render_kw={"placeholder": "Leave empty if you don't have one"})
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['png', 'jpg', 'jpeg'], 'Images only!')])
    short_bio = TextAreaField('Short Bio')
    submit = SubmitField('Move Forward')

class YourHabitsForm(FlaskForm):
    sleep = SelectField('Choose your sleeping habit', choices=[('Early Bird', 'Early Bird'), ('Night Owl', 'Night Owl'), ('Depends', 'Depends')])
    cleanliness = SelectField('Choose your level of cleanliness', choices=[('Tidy', 'Tidy'), ('Average', 'Average'), ('Messy', 'Messy')])
    relationship = SelectField('Are you in a relationship?', choices=[('Yes', 'Yes'), ('No', 'No'), ('Complicated', 'Complicated')])
    submit = SubmitField('Finish')

class UpdateAccountForm(FlaskForm):
    instagram_handle = StringField('Instagram Handle', render_kw={"placeholder": "Leave empty if you don't have one"})
    snapchat_handle = StringField('Snapchat Handle', render_kw={"placeholder": "Leave empty if you don't have one"})
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['png', 'jpg', 'jpeg'], 'Images only!')])
    short_bio = TextAreaField('Short Bio')
    sleep = SelectField('Choose your sleeping habit', choices=[('Early Bird', 'Early Bird'), ('Night Owl', 'Night Owl'), ('Depends', 'Depends')])
    cleanliness = SelectField('Choose your level of cleanliness', choices=[('Tidy', 'Tidy'), ('Average', 'Average'), ('Messy', 'Messy')])
    relationship = SelectField('Are you in a relationship?', choices=[('Yes', 'Yes'), ('No', 'No'), ('Complicated', 'Complicated')])
    password = PasswordField('Password', validators=[DataRequired()],render_kw={"placeholder": "New Password"})
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')], render_kw={"placeholder": "Confirm New Password"})
    submit = SubmitField('Finish')

class LoginForm(FlaskForm):
    #The code below for the email might need to change because the field is different...
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember = BooleanField('remember me')
    submit = SubmitField('Login')