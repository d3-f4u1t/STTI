from flask import render_template
from flask_login import login_required

from . import main_bp

@main_bp.route('/')
def home():
    return render_template('home.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@main_bp.route('/notifications')
@login_required
def notifications():
    return render_template('notifications.html')
