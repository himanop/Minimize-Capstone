from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, URLField, BooleanField, EmailField, FileField, DateField, SubmitField, SelectField
from flask_wtf.file import FileAllowed, FileRequired, FileField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
# from Minimize.models import User



class RegistrationForm(FlaskForm):
    #The variable names are how we are going to refer to the fields in the HTML code
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    #This is just a comment
    email = EmailField('Email')
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create Account')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username taken! Please choose different username.')
        
    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('Email taken! Please choose different email.')

class LoginForm(FlaskForm):
    #The code below for the email might need to change because the field is different...
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember = BooleanField('remember me')
    submit = SubmitField('Login')

class IntroduceYourselfForm(FlaskForm):
    instagram_handle = StringField('Instagram Handle')
    snapchat_handle = StringField('Snapchat Handle')
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    short_bio = TextAreaField('Short Bio')
    submit = SubmitField('Move Forward')

class YourHabitsForm(FlaskForm):
    sleep = SelectField('Choose your sleeping habit', choices=[('early_bird', 'Early Bird'), ('night_owl', 'Night Owl'), ('depends', 'Depends')])
    cleanliness = SelectField('Choose your level of cleanliness', choices=[('tidy', 'Tidy'), ('average', 'Average'), ('messy', 'Messy')])
    relationship = SelectField('Are you in a relationship?', choices=[('yes', 'Yes'), ('no', 'No'), ('complicated', 'Complicated')])
    submit = SubmitField('Finish')