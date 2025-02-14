from Minimize import db, login_manager
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

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

class User_Socials(db.Model, UserMixin):
    __tablename__ = 'user_socials'
    id = db.Column(db.Integer, primary_key=True)
    instagram_handle = db.Column(db.String(50), nullable=True)
    snapchat_handle = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(15), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

class User_Habits(db.Model, UserMixin):
    __tablename__ = 'user_habits'
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f"User('{self.first_name},{self.last_name},{self.username}', '{self.email}', '{self.image_file}')"
    
# class User_Social():
#     pro_pic = db.Column(db.String(20), nullable=False, default = 'default.jpeg')
#     short_bio = db.Column(db.Text, nullable=False)
#     insta_link = db.Column(db.String(40), nullable=True)
#     snap_link = db.Column(db.String(40), nullable=True)