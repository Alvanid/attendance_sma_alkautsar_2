from werkzeug.security import check_password_hash
from ..database import execute_db, query_db
from datetime import datetime

def authenticate_user(username, password):
    """Memverifikasi kredensial pengguna."""
    user = query_db('SELECT * FROM users WHERE username = ? AND status = 1', [username], one=True)
    if user and check_password_hash(user['password_hash'], password):
        # Update waktu login terakhir
        execute_db('UPDATE users SET last_login = ? WHERE id = ?', [datetime.now(), user['id']])
        return user
    return None

def log_activity(user_id, action, description, ip_address='127.0.0.1'):
    """Mencatat aktivitas ke tabel activity_logs."""
    execute_db(
        'INSERT INTO activity_logs (user_id, action, description, ip_address) VALUES (?, ?, ?, ?)',
        [user_id, action, description, ip_address]
    )