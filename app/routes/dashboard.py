from flask import Blueprint, render_template, redirect, url_for, session
from app.database import get_conn
from app.auth_helpers import login_required, get_current_user
from app import get_db_path
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def home():
    conn = get_conn(get_db_path())
    user = get_current_user(conn)
    today = datetime.now().strftime('%A')
    now = datetime.now()

    if user['role'] == 'teacher':
        today_classes = conn.execute(
            "SELECT t.*, u.full_name as teacher_name, u.username as teacher_username FROM timetable_entries t JOIN users u ON t.teacher_id=u.id WHERE t.day_of_week=? AND t.teacher_id=? ORDER BY t.start_time",
            (today, user['id'])
        ).fetchall()
    else:
        dept = user.get('department', '')
        if dept:
            today_classes = conn.execute(
                "SELECT t.*, u.full_name as teacher_name, u.username as teacher_username FROM timetable_entries t JOIN users u ON t.teacher_id=u.id WHERE t.day_of_week=? AND t.department=? ORDER BY t.start_time",
                (today, dept)
            ).fetchall()
        else:
            today_classes = conn.execute(
                "SELECT t.*, u.full_name as teacher_name, u.username as teacher_username FROM timetable_entries t JOIN users u ON t.teacher_id=u.id WHERE t.day_of_week=? ORDER BY t.start_time",
                (today,)
            ).fetchall()

    today_classes = [dict(r) for r in today_classes]

    all_notifs = conn.execute(
        "SELECT * FROM notifications WHERE (target_role='all' OR target_role=?) AND is_active=1",
        (user['role'],)
    ).fetchall()

    read_rows = conn.execute("SELECT notification_id FROM notification_reads WHERE user_id=?", (user['id'],)).fetchall()
    read_ids = {r['notification_id'] for r in read_rows}
    unread_count = sum(1 for n in all_notifs if n['id'] not in read_ids)

    total_classes_today = len(today_classes)
    cancelled_today = sum(1 for c in today_classes if c['status'] == 'cancelled')
    active_today = sum(1 for c in today_classes if c['status'] in ('started', 'scheduled'))

    total_teachers = conn.execute("SELECT COUNT(*) FROM users WHERE role='teacher'").fetchone()[0]
    total_students = conn.execute("SELECT COUNT(*) FROM users WHERE role='student'").fetchone()[0]

    recent_notifs = conn.execute(
        "SELECT n.*, u.full_name as sender_name, u.username as sender_username FROM notifications n JOIN users u ON n.sender_id=u.id WHERE (n.target_role='all' OR n.target_role=?) AND n.is_active=1 ORDER BY n.created_at DESC LIMIT 5",
        (user['role'],)
    ).fetchall()
    recent_notifs = [dict(r) for r in recent_notifs]
    conn.close()

    return render_template('dashboard/home.html',
        user=user,
        today=today,
        today_classes=today_classes,
        unread_count=unread_count,
        total_classes_today=total_classes_today,
        cancelled_today=cancelled_today,
        active_today=active_today,
        total_teachers=total_teachers,
        total_students=total_students,
        recent_notifs=recent_notifs,
        read_ids=read_ids,
        now=now
    )


@dashboard_bp.route('/analytics')
@login_required
def analytics():
    conn = get_conn(get_db_path())
    user = get_current_user(conn)
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    day_counts = {}
    for day in days:
        count = conn.execute("SELECT COUNT(*) FROM timetable_entries WHERE day_of_week=?", (day,)).fetchone()[0]
        day_counts[day] = count

    status_counts = {}
    for s in ['scheduled', 'started', 'delayed', 'cancelled']:
        count = conn.execute("SELECT COUNT(*) FROM timetable_entries WHERE status=?", (s,)).fetchone()[0]
        status_counts[s] = count
    conn.close()

    return render_template('dashboard/analytics.html',
        user=user,
        day_counts=day_counts,
        status_counts=status_counts
    )
