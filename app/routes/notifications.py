from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session
from app.database import get_conn
from app.auth_helpers import login_required, get_current_user
from app import get_db_path

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/')
@login_required
def view():
    conn = get_conn(get_db_path())
    user = get_current_user(conn)

    notifs = conn.execute(
        "SELECT n.*, u.full_name as sender_name, u.username as sender_username FROM notifications n JOIN users u ON n.sender_id=u.id WHERE (n.target_role='all' OR n.target_role=?) AND n.is_active=1 ORDER BY n.created_at DESC",
        (user['role'],)
    ).fetchall()
    notifs = [dict(r) for r in notifs]

    read_rows = conn.execute("SELECT notification_id FROM notification_reads WHERE user_id=?", (user['id'],)).fetchall()
    read_ids = {r['notification_id'] for r in read_rows}
    conn.close()

    return render_template('notifications/view.html', notifications=notifs, read_ids=read_ids, user=user)


@notifications_bp.route('/mark_read/<int:notif_id>', methods=['POST'])
@login_required
def mark_read(notif_id):
    conn = get_conn(get_db_path())
    user = get_current_user(conn)
    try:
        conn.execute(
            "INSERT OR IGNORE INTO notification_reads (notification_id, user_id) VALUES (?,?)",
            (notif_id, user['id'])
        )
        conn.commit()
    except Exception:
        pass
    conn.close()
    return jsonify({'success': True})


@notifications_bp.route('/mark_all_read', methods=['POST'])
@login_required
def mark_all_read():
    conn = get_conn(get_db_path())
    user = get_current_user(conn)

    notifs = conn.execute(
        "SELECT id FROM notifications WHERE (target_role='all' OR target_role=?) AND is_active=1",
        (user['role'],)
    ).fetchall()

    for n in notifs:
        conn.execute(
            "INSERT OR IGNORE INTO notification_reads (notification_id, user_id) VALUES (?,?)",
            (n['id'], user['id'])
        )

    conn.commit()
    conn.close()
    flash('All notifications marked as read.', 'success')
    return redirect(url_for('notifications.view'))


@notifications_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    conn = get_conn(get_db_path())
    user = get_current_user(conn)

    if user['role'] != 'teacher':
        conn.close()
        flash('Only teachers can send notifications.', 'danger')
        return redirect(url_for('notifications.view'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        message = request.form.get('message', '').strip()
        notif_type = request.form.get('notification_type', 'info')
        target_role = request.form.get('target_role', 'all')

        conn.execute(
            "INSERT INTO notifications (title, message, notification_type, target_role, sender_id) VALUES (?,?,?,?,?)",
            (title, message, notif_type, target_role, user['id'])
        )
        conn.commit()
        conn.close()
        flash('Notification sent!', 'success')
        return redirect(url_for('notifications.view'))

    conn.close()
    return render_template('notifications/create.html', user=user)


@notifications_bp.route('/unread_count')
@login_required
def unread_count():
    conn = get_conn(get_db_path())
    user = get_current_user(conn)

    notifs = conn.execute(
        "SELECT id FROM notifications WHERE (target_role='all' OR target_role=?) AND is_active=1",
        (user['role'],)
    ).fetchall()
    read_rows = conn.execute("SELECT notification_id FROM notification_reads WHERE user_id=?", (user['id'],)).fetchall()
    read_ids = {r['notification_id'] for r in read_rows}
    count = sum(1 for n in notifs if n['id'] not in read_ids)
    conn.close()
    return jsonify({'count': count})
