from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session
from app.database import get_conn
from app.auth_helpers import login_required, get_current_user
from app import get_db_path
from datetime import datetime

timetable_bp = Blueprint('timetable', __name__)
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

@timetable_bp.route('/')
@login_required
def view():
    conn = get_conn(get_db_path())
    user = get_current_user(conn)

    if user['role'] == 'teacher':
        entries = conn.execute(
            "SELECT t.*, u.full_name as teacher_name, u.username as teacher_username FROM timetable_entries t JOIN users u ON t.teacher_id=u.id WHERE t.teacher_id=? ORDER BY t.start_time",
            (user['id'],)
        ).fetchall()
    else:
        dept = user.get('department', '')
        if dept:
            entries = conn.execute(
                "SELECT t.*, u.full_name as teacher_name, u.username as teacher_username FROM timetable_entries t JOIN users u ON t.teacher_id=u.id WHERE t.department=? ORDER BY t.start_time",
                (dept,)
            ).fetchall()
        else:
            entries = conn.execute(
                "SELECT t.*, u.full_name as teacher_name, u.username as teacher_username FROM timetable_entries t JOIN users u ON t.teacher_id=u.id ORDER BY t.start_time"
            ).fetchall()

    conn.close()
    entries = [dict(r) for r in entries]

    timetable = {day: [] for day in DAYS}
    for entry in entries:
        if entry['day_of_week'] in timetable:
            timetable[entry['day_of_week']].append(entry)

    today = datetime.now().strftime('%A')
    return render_template('timetable/view.html', timetable=timetable, days=DAYS, today=today, user=user)


@timetable_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    conn = get_conn(get_db_path())
    user = get_current_user(conn)

    if user['role'] != 'teacher':
        conn.close()
        flash('Only teachers can create timetable entries.', 'danger')
        return redirect(url_for('timetable.view'))

    if request.method == 'POST':
        subject = request.form.get('subject', '').strip()
        day = request.form.get('day_of_week')
        start_str = request.form.get('start_time')
        end_str = request.form.get('end_time')
        room = request.form.get('room', '').strip()
        department = request.form.get('department', user.get('department') or '').strip()

        if not subject or not day or not start_str or not end_str:
            flash('Please fill all required fields.', 'danger')
            conn.close()
            return render_template('timetable/create.html', days=DAYS, user=user)

        if start_str >= end_str:
            flash('End time must be after start time.', 'danger')
            conn.close()
            return render_template('timetable/create.html', days=DAYS, user=user)

        conn.execute(
            "INSERT INTO timetable_entries (subject, day_of_week, start_time, end_time, room, department, teacher_id) VALUES (?,?,?,?,?,?,?)",
            (subject, day, start_str, end_str, room, department, user['id'])
        )
        conn.commit()
        conn.close()
        flash(f'Class "{subject}" added to {day}!', 'success')
        return redirect(url_for('timetable.view'))

    conn.close()
    return render_template('timetable/create.html', days=DAYS, user=user)


@timetable_bp.route('/update_status/<int:entry_id>', methods=['POST'])
@login_required
def update_status(entry_id):
    conn = get_conn(get_db_path())
    user = get_current_user(conn)

    if user['role'] != 'teacher':
        conn.close()
        return jsonify({'error': 'Unauthorized'}), 403

    entry = conn.execute("SELECT * FROM timetable_entries WHERE id=?", (entry_id,)).fetchone()
    if not entry or entry['teacher_id'] != user['id']:
        conn.close()
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json(silent=True) or {}
    new_status = data.get('status') or request.form.get('status')
    valid_statuses = ['scheduled', 'started', 'delayed', 'cancelled']

    if new_status not in valid_statuses:
        conn.close()
        return jsonify({'error': 'Invalid status'}), 400

    conn.execute("UPDATE timetable_entries SET status=? WHERE id=?", (new_status, entry_id))

    if new_status in ('delayed', 'cancelled'):
        msg_map = {
            'delayed': f'Class "{entry["subject"]}" on {entry["day_of_week"]} has been delayed.',
            'cancelled': f'Class "{entry["subject"]}" on {entry["day_of_week"]} has been cancelled.'
        }
        conn.execute(
            "INSERT INTO notifications (title, message, notification_type, target_role, sender_id) VALUES (?,?,?,?,?)",
            (f'Class {new_status.title()}: {entry["subject"]}', msg_map[new_status],
             'warning' if new_status == 'delayed' else 'danger', 'student', user['id'])
        )

    conn.commit()
    conn.close()
    return jsonify({'success': True, 'status': new_status})


@timetable_bp.route('/delete/<int:entry_id>', methods=['POST'])
@login_required
def delete(entry_id):
    conn = get_conn(get_db_path())
    user = get_current_user(conn)

    if user['role'] != 'teacher':
        conn.close()
        flash('Unauthorized.', 'danger')
        return redirect(url_for('timetable.view'))

    entry = conn.execute("SELECT * FROM timetable_entries WHERE id=?", (entry_id,)).fetchone()
    if not entry or entry['teacher_id'] != user['id']:
        conn.close()
        flash('You can only delete your own entries.', 'danger')
        return redirect(url_for('timetable.view'))

    conn.execute("DELETE FROM timetable_entries WHERE id=?", (entry_id,))
    conn.commit()
    conn.close()
    flash('Timetable entry deleted.', 'success')
    return redirect(url_for('timetable.view'))
