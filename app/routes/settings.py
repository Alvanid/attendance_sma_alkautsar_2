from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from ..utils.decorators import super_admin_required, staff_required
from ..database import query_db, execute_db
from ..services.auth_service import log_activity

settings_bp = Blueprint('settings', __name__, url_prefix='/settings', template_folder='../templates/settings')

@settings_bp.route('/')
@login_required
@super_admin_required
def index():
    """Halaman Pengaturan Sekolah dan Jam Absensi."""
    settings = {row['key']: row['value'] for row in query_db("SELECT key, value FROM school_settings")}
    return render_template('settings/index.html', settings=settings)

@settings_bp.route('/update', methods=['POST'])
@login_required
@super_admin_required
def update():
    """Menyimpan perubahan pengaturan ke database."""
    form_data = request.form.to_dict()
    try:
        for key, value in form_data.items():
            if key.startswith('csrf'): continue # Abaikan CSRF token
            execute_db("UPDATE school_settings SET value = ? WHERE key = ?", [value, key])
            
        log_activity(current_user.id, 'UPDATE_SETTINGS', 'Memperbarui pengaturan sekolah dan jam absensi', request.remote_addr)
        flash('Pengaturan sistem berhasil diperbarui.', 'success')
    except Exception as e:
        flash(f'Gagal memperbarui pengaturan: {str(e)}', 'danger')
        
    return redirect(url_for('settings.index'))

@settings_bp.route('/logs')
@login_required
@super_admin_required
def logs():
    """Halaman Activity Log (Audit Trail)."""
    logs = query_db('''
        SELECT l.*, u.username, u.full_name 
        FROM activity_logs l
        LEFT JOIN users u ON l.user_id = u.id
        ORDER BY l.created_at DESC
        LIMIT 500
    ''')
    return render_template('settings/logs.html', logs=logs)

@settings_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@staff_required
def profile():
    """Halaman Profil dan Ganti Password."""
    if request.method == 'POST':
        old_pass = request.form.get('old_password')
        new_pass = request.form.get('new_password')
        confirm_pass = request.form.get('confirm_password')
        
        user = query_db("SELECT password_hash FROM users WHERE id = ?", [current_user.id], one=True)
        
        if not check_password_hash(user['password_hash'], old_pass):
            flash('Password lama yang Anda masukkan salah.', 'danger')
        elif new_pass != confirm_pass:
            flash('Konfirmasi password baru tidak cocok.', 'danger')
        elif len(new_pass) < 6:
            flash('Password baru minimal 6 karakter.', 'warning')
        else:
            hashed = generate_password_hash(new_pass)
            execute_db("UPDATE users SET password_hash = ? WHERE id = ?", [hashed, current_user.id])
            log_activity(current_user.id, 'CHANGE_PASSWORD', 'Berhasil mengubah password akun', request.remote_addr)
            flash('Password berhasil diubah! Silakan login kembali.', 'success')
            return redirect(url_for('auth.logout'))

    return render_template('settings/profile.html')