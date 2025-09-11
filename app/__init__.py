from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .extentions import db, login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Redirects to login page if not authenticated

    from app.main.routes import main_bp
    from app.auth.routes import auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    return app
