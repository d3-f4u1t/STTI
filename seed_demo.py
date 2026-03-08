"""Run this script to populate demo data: python seed_demo.py"""
from app import create_app
from app.database import get_conn, init_db
from app.auth_helpers import hash_password
import os

app = create_app()

with app.app_context():
    from app import get_db_path
    conn = get_conn(get_db_path())

    # Demo teacher
    if not conn.execute("SELECT id FROM users WHERE email='teacher@demo.com'").fetchone():
        conn.execute(
            "INSERT INTO users (username, email, full_name, department, role, password_hash) VALUES (?,?,?,?,?,?)",
            ('prof_smith', 'teacher@demo.com', 'Prof. Smith', 'Computer Science', 'teacher', hash_password('demo123'))
        )

    # Demo student
    if not conn.execute("SELECT id FROM users WHERE email='student@demo.com'").fetchone():
        conn.execute(
            "INSERT INTO users (username, email, full_name, department, role, password_hash) VALUES (?,?,?,?,?,?)",
            ('alice_j', 'student@demo.com', 'Alice Jones', 'Computer Science', 'student', hash_password('demo123'))
        )

    conn.commit()
    teacher = conn.execute("SELECT id FROM users WHERE email='teacher@demo.com'").fetchone()

    # Classes
    classes = [
        ('Data Structures', 'Monday', '09:00', '10:30', 'Lab 3', 'Computer Science', 'started'),
        ('Algorithms', 'Monday', '11:00', '12:30', 'Room 201', 'Computer Science', 'scheduled'),
        ('Database Systems', 'Tuesday', '10:00', '11:30', 'Lab 2', 'Computer Science', 'scheduled'),
        ('Operating Systems', 'Wednesday', '09:00', '10:30', 'Room 301', 'Computer Science', 'delayed'),
        ('Computer Networks', 'Thursday', '14:00', '15:30', 'Lab 1', 'Computer Science', 'scheduled'),
        ('Software Engineering', 'Friday', '11:00', '12:30', 'Room 102', 'Computer Science', 'cancelled'),
    ]

    for cls in classes:
        if not conn.execute("SELECT id FROM timetable_entries WHERE subject=? AND day_of_week=?", (cls[0], cls[1])).fetchone():
            conn.execute(
                "INSERT INTO timetable_entries (subject, day_of_week, start_time, end_time, room, department, status, teacher_id) VALUES (?,?,?,?,?,?,?,?)",
                (*cls, teacher['id'])
            )

    # Notifications
    notifs = [
        ('Welcome to STTI!', 'The Student Teacher Time Interface is now live. Check your timetable for this week.', 'info', 'all'),
        ('OS Class Delayed', 'Operating Systems class on Wednesday has been delayed by 30 minutes.', 'warning', 'student'),
        ('SE Class Cancelled', 'Software Engineering class on Friday has been cancelled. Stay tuned for rescheduling.', 'danger', 'student'),
    ]
    for n in notifs:
        if not conn.execute("SELECT id FROM notifications WHERE title=?", (n[0],)).fetchone():
            conn.execute(
                "INSERT INTO notifications (title, message, notification_type, target_role, sender_id) VALUES (?,?,?,?,?)",
                (*n, teacher['id'])
            )

    conn.commit()
    conn.close()
    print("✅ Demo data seeded successfully!")
    print("   Teacher login: teacher@demo.com / demo123")
    print("   Student login: student@demo.com / demo123")
