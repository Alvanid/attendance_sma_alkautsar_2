import os
from flask import Flask, request, jsonify, flash, redirect, url_for
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect, CSRFError
from config import config
from .database import close_db, query_db
from .models.user import User

# Inisialisasi Extension di luar factory agar bisa di-import module lain jika perlu
login_manager = LoginManager()
login_manager.login_view = 'auth.login' 
login_manager.login_message_category = 'info'
login_manager.login_message = 'Silakan login terlebih dahulu untuk mengakses halaman ini.'

csrf = CSRFProtect()

def create_app(config_name='default'):
    """
    Application Factory Pattern
    """
    app = Flask(__name__)
    
    # Load Config
    app.config.from_object(config[config_name])
    
    # Pastikan folder static untuk upload dan QR ada
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['QR_FOLDER'], exist_ok=True)
    
    # Inisialisasi Extension ke App
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Register Database Teardown (menutup koneksi DB di akhir request)
    app.teardown_appcontext(close_db)
    
    # ==========================================
    # IMPORT & REGISTER BLUEPRINTS (ROUTES)
    # ==========================================
    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp
    from .routes.students import students_bp
    from .routes.classes import classes_bp
    from .routes.attendance import attendance_bp
    from .routes.qrcode import qrcode_bp
    from .routes.reports import reports_bp
    from .routes.settings import settings_bp
    from .routes.users import users_bp  # <-- Penting: Modul Manajemen User (Tahap 10)
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(classes_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(qrcode_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(users_bp)   # <-- Pastikan ini terdaftar
    
    # ==========================================
    # FLASK-LOGIN: USER LOADER
    # ==========================================
    @login_manager.user_loader
    def load_user(user_id):
        user_data = query_db('SELECT * FROM users WHERE id = ?', [user_id], one=True)
        if user_data:
            return User(
                id=user_data['id'],
                username=user_data['username'],
                full_name=user_data['full_name'],
                role=user_data['role'],
                status=user_data['status'],
                password_hash=user_data['password_hash']
            )
        return None

    # ==========================================
    # CUSTOM ERROR HANDLER (CSRF EXPIRED)
    # ==========================================
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        # Jika request berasal dari AJAX (seperti Scanner QR Code)
        if request.is_json or request.path.startswith('/attendance/process'):
            return jsonify({
                'success': False, 
                'message': 'Sesi keamanan (CSRF) telah berakhir. Silakan refresh halaman (F5) pada tablet/laptop untuk melanjutkan scan.'
            }), 400
            
        # Jika request berasal dari Form Submit biasa (HTML)
        flash('Sesi Anda telah berakhir atau token keamanan tidak valid. Silakan refresh halaman dan coba lagi.', 'danger')
        return redirect(request.referrer or url_for('auth.login')), 302

    return app