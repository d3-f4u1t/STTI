from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import Timetable, Notification
from app.extentions import db , login_manager

timetable_bp = Blueprint('timetable', __name__, template_folder='templates')

@timetable_bp.route('/dashboard')
def dashboard():
    timetables = Timetable.query.all()
    return render_template('timetable_dashboard.html', timetables=timetables)

@timetable_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        department = request.form.get('department')
        semester = request.form.get('semester')
        data = request.form.get('data')  # Could be JSON string

        new_tt = Timetable(department=department, semester=semester, data=data)
        db.session.add(new_tt)
        db.session.commit()

        flash('Timetable created successfully', 'success')
        return redirect(url_for('timetable.dashboard'))

    return render_template('create_timetable.html')



