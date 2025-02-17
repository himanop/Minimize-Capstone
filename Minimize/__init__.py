from flask import Flask
from config import Config
from Minimize.extensions import db, bcrypt, login_manager

app = None  # ✅ Initialize app as None

print("Inside __init__.py")

def create_app():
    global app
    print("Inside create_app()")
    app = Flask(__name__)
    app.config.from_object(Config)
    print("Before db.init_app(app)")
    db.init_app(app)
    print("After db.init_app(app)")
    bcrypt.init_app(app)
    print("After bcrypt.init_app(app)")
    login_manager.init_app(app)
    print("After login_manager.init_app(app)")
    login_manager.login_view = "routes.login"
    login_manager.login_message_category = "info"
    print("After login_manager.login_view")
    print("After Minimize.routes import")  # ✅ Import routes AFTER app is created
    # app.register_blueprint(routes)
    print(id(app))
    return app  # ✅ Return the Flask app instance

# from Minimize import routes  # ✅ Import routes AFTER app is created

from Minimize.models import User  # ✅ Import models AFTER initializing extensions
# app.register_blueprint(routes)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
