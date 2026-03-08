from flask import Flask
from config import Config
import sqlite3
import os

DB_PATH = None

def get_db_path():
    return DB_PATH

def create_app(config_class=Config):
    global DB_PATH
    app = Flask(__name__)
    app.config.from_object(config_class)

    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'instance', 'stti.db')
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    from app.database import init_db
    init_db(DB_PATH)

    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.timetable import timetable_bp
    from app.routes.notifications import notifications_bp
    from app.routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(timetable_bp, url_prefix='/timetable')
    app.register_blueprint(notifications_bp, url_prefix='/notifications')

    return app
