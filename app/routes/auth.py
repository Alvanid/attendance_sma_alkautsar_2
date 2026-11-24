from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from ..services.auth_service import authenticate_user, log_activity
from ..models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='../templates/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Jika sudah login, langsung lempar ke dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user_data = authenticate_user(username, password)
        
        if user_data:
            user_obj = User(
                id=user_data['id'], username=user_data['username'], 
                full_name=user_data['full_name'], role=user_data['role'], 
                status=user_data['status']
            )
            login_user(user_obj, remember=remember)
            log_activity(user_data['id'], 'LOGIN', f'User {username} berhasil login', request.remote_addr)
            
            flash('Login berhasil! Selamat datang di AL-KAUTSAR ATTENDANCE SYSTEM.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            log_activity(None, 'LOGIN_FAILED', f'Percobaan login gagal untuk username: {username}', request.remote_addr)
            flash('Username atau Password salah, atau akun tidak aktif.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    log_activity(current_user.id, 'LOGOUT', f'User {current_user.username} logout', request.remote_addr)
    logout_user()
    flash('Anda telah berhasil logout.', 'info')
    return redirect(url_for('auth.login'))