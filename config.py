import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables dari file .env
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Konfigurasi Dasar (Base Config)"""
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-alkautsar-2024'
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 43200 
    
    # Database
    # Menggunakan absolute path ke folder 'instance'
    DATABASE = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'attendance.db')
        
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False # Set True jika menggunakan HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Upload Folders
    UPLOAD_FOLDER = os.path.join(basedir, 'app/static/images')
    QR_FOLDER = os.path.join(basedir, 'app/static/qr_codes')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16MB Max upload
    
    # Pagination
    POSTS_PER_PAGE = 20

class DevelopmentConfig(Config):
    """Konfigurasi Development"""
    DEBUG = True
    TESTING = False
    # Tambahkan konfigurasi khusus dev jika perlu

class ProductionConfig(Config):
    """Konfigurasi Production"""
    DEBUG = False
    TESTING = False
    # Di production, pastikan SECRET_KEY diambil dari ENV yang kuat

# Dictionary untuk memudahkan pemanggilan
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}