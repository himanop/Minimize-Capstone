from Minimize import app
from flask_login import UserMixin
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from Minimize.extensions import db, bcrypt, login_manager
from flask_login import UserMixin
# db = SQLAlchemy()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(15), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # One-to-One Relationship with User_Socials and User_Habits
    socials = db.relationship('User_Socials', back_populates='user', uselist=False, cascade="all, delete-orphan")
    habits = db.relationship('User_Habits', back_populates='user', uselist=False, cascade="all, delete-orphan")

class User_Socials(db.Model):
    __tablename__ = 'user_socials'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    instagram_handle = db.Column(db.String(50), nullable=True)
    snapchat_handle = db.Column(db.String(50), nullable=True)
    profile_picture = db.Column(db.String(100), nullable=False, default='default.jpeg')
    short_bio = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship back to User
    user = db.relationship('User', back_populates='socials')

class User_Habits(db.Model):
    __tablename__ = 'user_habits'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    sleep = db.Column(db.String(15), nullable=False)
    cleanliness = db.Column(db.String(15), nullable=False)
    relationship = db.Column(db.String(15), nullable=False)

    # Relationship back to User
    user = db.relationship('User', back_populates='habits')

    def __repr__(self):
        return f"User_Habits('{self.sleep}', '{self.cleanliness}', '{self.relationship}')"
