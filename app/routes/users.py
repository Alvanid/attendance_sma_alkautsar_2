from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from ..utils.decorators import super_admin_required
from ..database import query_db, execute_db
from ..services.auth_service import log_activity

users_bp = Blueprint('users', __name__, url_prefix='/users', template_folder='../templates/users')

@users_bp.route('/')
@login_required
@super_admin_required
def index():
    users = query_db("SELECT * FROM users ORDER BY created_at DESC")
    return render_template('users/index.html', users=users)

@users_bp.route('/add', methods=['POST'])
@login_required
@super_admin_required
def add():
    username = request.form.get('username')
    full_name = request.form.get('full_name')
    role = request.form.get('role')
    
    # Password default untuk user baru
    default_pass = generate_password_hash('alkautsar123')
    
    try:
        execute_db('''
            INSERT INTO users (username, full_name, role, password_hash, status)
            VALUES (?, ?, ?, ?, 1)
        ''', [username, full_name, role, default_pass])
        log_activity(current_user.id, 'ADD_USER', f'Menambahkan user baru: {username}', request.remote_addr)
        flash(f'User {username} berhasil ditambahkan. Password default: alkautsar123', 'success')
    except Exception as e:
        flash(f'Gagal menambahkan user (Username mungkin sudah dipakai): {str(e)}', 'danger')
        
    return redirect(url_for('users.index'))

@users_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
@super_admin_required
def edit(id):
    full_name = request.form.get('full_name')
    role = request.form.get('role')
    status = 1 if request.form.get('status') == 'on' else 0
    
    try:
        execute_db("UPDATE users SET full_name = ?, role = ?, status = ? WHERE id = ?", 
                   [full_name, role, status, id])
        log_activity(current_user.id, 'EDIT_USER', f'Mengupdate data user ID: {id}', request.remote_addr)
        flash('Data pengguna berhasil diperbarui.', 'success')
    except Exception as e:
        flash(f'Gagal memperbarui data: {str(e)}', 'danger')
        
    return redirect(url_for('users.index'))

@users_bp.route('/reset-password/<int:id>')
@login_required
@super_admin_required
def reset_password(id):
    default_pass = generate_password_hash('alkautsar123')
    execute_db("UPDATE users SET password_hash = ? WHERE id = ?", [default_pass, id])
    log_activity(current_user.id, 'RESET_PASSWORD', f'Mereset password user ID: {id}', request.remote_addr)
    flash('Password berhasil direset ke default (alkautsar123).', 'info')
    return redirect(url_for('users.index'))