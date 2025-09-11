from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Notification 

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('home.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)



main = Blueprint('main', __name__)

@main.route('/')
def home():
    notifications = Notification.query.all()
    return render_template('home.html', notifications=notifications)

@main.route('/remove_notification', methods=['POST'])
def remove_notification():
    notif_id = request.form.get('id')
    notif = Notification.query.get(notif_id)
    if notif:
        db.session.delete(notif)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})
