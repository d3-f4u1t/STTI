from flask import session, redirect, url_for, g
from functools import wraps
import hashlib
import os

def hash_password(password):
    salt = os.urandom(16).hex()
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${hashed}"

def check_password(password_hash, password):
    try:
        salt, hashed = password_hash.split('$')
        return hashlib.sha256((salt + password).encode()).hexdigest() == hashed
    except Exception:
        return False

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login', next=url_for(f.__module__.split('.')[-1] + '.' + f.__name__)))
        return f(*args, **kwargs)
    return decorated

def get_current_user(conn):
    user_id = session.get('user_id')
    if not user_id:
        return None
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return dict(row) if row else None
