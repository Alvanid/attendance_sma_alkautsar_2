import os

base_dir = 'app/routes'
os.makedirs(base_dir, exist_ok=True)

# 1. Buat __init__.py agar folder dikenali sebagai Python Package
open(os.path.join(base_dir, '__init__.py'), 'w').close()
print("Created __init__.py")

# 2. Definisi konten untuk setiap blueprint
files = {
    'auth.py': "from flask import Blueprint\nauth_bp = Blueprint('auth', __name__, url_prefix='/auth')\n\n@auth_bp.route('/login')\ndef login():\n    return 'Halaman Login (Tahap 4)'",
    
    'dashboard.py': "from flask import Blueprint\ndashboard_bp = Blueprint('dashboard', __name__, url_prefix='/')\n\n@dashboard_bp.route('/')\ndef index():\n    return 'Dashboard Utama (Tahap 5)'",
    
    'students.py': "from flask import Blueprint\nstudents_bp = Blueprint('students', __name__, url_prefix='/students')\n\n@students_bp.route('/')\ndef index():\n    return 'Manajemen Data Siswa (Tahap 6)'",
    
    'classes.py': "from flask import Blueprint\nclasses_bp = Blueprint('classes', __name__, url_prefix='/classes')\n\n@classes_bp.route('/')\ndef index():\n    return 'Manajemen Kelas (Tahap 6)'",
    
    'attendance.py': "from flask import Blueprint\nattendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')\n\n@attendance_bp.route('/')\ndef index():\n    return 'Sistem Absensi (Tahap 8)'",
    
    'qrcode.py': "from flask import Blueprint\nqrcode_bp = Blueprint('qrcode', __name__, url_prefix='/qrcode')\n\n@qrcode_bp.route('/')\ndef index():\n    return 'Generator QR Code (Tahap 7)'",
    
    'reports.py': "from flask import Blueprint\nreports_bp = Blueprint('reports', __name__, url_prefix='/reports')\n\n@reports_bp.route('/')\ndef index():\n    return 'Laporan & Rekap (Tahap 9)'",
    
    'settings.py': "from flask import Blueprint\nsettings_bp = Blueprint('settings', __name__, url_prefix='/settings')\n\n@settings_bp.route('/')\ndef index():\n    return 'Pengaturan Sistem (Tahap 10)'"
}

# 3. Generate seluruh file
for fname, content in files.items():
    filepath = os.path.join(base_dir, fname)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created {fname}")

print("\n✅ Semua file route berhasil dibuat!")