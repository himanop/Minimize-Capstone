from flask import Flask
from datetime import datetime
#URI is where the DB is located
# from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
# from flask_login import LoginManager

app = Flask(__name__)
#Flask-SQLAlchemy relies on the application context to access configuration settings and other necessary resources.
#Need to import "app" in the script when trying to run the create_all() function to make the DB
app.config['SECRET_KEY'] = 'd014d81f366194e43f3bd4ed8e5b81a7'
#The three slashes below represent the location of the site.db relative to this file.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
# login_manager = LoginManager(app)

from Minimize import routes
from Minimize import app
