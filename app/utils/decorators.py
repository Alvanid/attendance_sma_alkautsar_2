from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user

def role_required(*allowed_roles):
    """Decorator untuk membatasi akses berdasarkan role."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Anda harus login terlebih dahulu.', 'warning')
                return redirect(url_for('auth.login'))
            if current_user.role not in allowed_roles:
                abort(403) # HTTP 403 Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Pre-defined decorators untuk kemudahan penggunaan
def super_admin_required(f):
    return role_required('super_admin')(f)

def admin_required(f):
    return role_required('super_admin', 'admin')(f)

def staff_required(f):
    """Untuk Admin, Super Admin, dan Guru"""
    return role_required('super_admin', 'admin', 'guru')(f)