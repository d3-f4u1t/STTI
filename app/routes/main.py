from flask import Blueprint, render_template, redirect, url_for, session
from app.database import get_conn
from app import get_db_path

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard.home'))
    return render_template('index.html')
