from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from ..utils.decorators import staff_required
from ..database import query_db, execute_db
from datetime import datetime

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance', template_folder='../templates/attendance')

@attendance_bp.route('/scan')
@login_required
@staff_required
def scan():
    """Halaman utama untuk pemindaian QR Code."""
    return render_template('attendance/scan.html')

@attendance_bp.route('/process', methods=['POST'])
@login_required
@staff_required
def process():
    """API Endpoint untuk memproses token QR yang dipindai."""
    data = request.get_json()
    token = data.get('token')
    
    if not token:
        return jsonify({'success': False, 'message': 'Token tidak valid.'}), 400
        
    # 1. Validasi Token QR
    qr = query_db("SELECT student_id FROM qr_tokens WHERE token = ? AND is_active = 1", [token], one=True)
    if not qr:
        return jsonify({'success': False, 'message': 'QR Code tidak terdaftar atau tidak aktif.'}), 404
        
    student_id = qr['student_id']
    
    # 2. Cek Data Siswa
    student = query_db('''
        SELECT s.full_name, s.nis, c.name as class_name 
        FROM students s 
        JOIN classes c ON s.class_id = c.id 
        WHERE s.id = ? AND s.status = 1
    ''', [student_id], one=True)
    
    if not student:
        return jsonify({'success': False, 'message': 'Siswa tidak ditemukan atau tidak aktif.'}), 404
        
    # 3. Cek Duplikasi Absensi Hari Ini
    today = datetime.now().strftime('%Y-%m-%d')
    existing = query_db("SELECT id FROM attendance WHERE student_id = ? AND date = ?", [student_id, today], one=True)
    if existing:
        return jsonify({
            'success': False, 
            'message': f"{student['full_name']} sudah melakukan absensi hari ini.",
            'student': student
        }), 409 # HTTP 409 Conflict
        
    # 4. Ambil Pengaturan Jam dari Database
    settings = {row['key']: row['value'] for row in query_db("SELECT key, value FROM school_settings")}
    on_time_limit = settings.get('attendance_on_time', '07:00')
    end_limit = settings.get('attendance_end', '08:00')
    
    now = datetime.now()
    time_in = now.strftime('%H:%M:%S')
    current_time = now.strftime('%H:%M')
    
    # 5. Tentukan Status Otomatis
    status = 'Hadir'
    if current_time > on_time_limit and current_time <= end_limit:
        status = 'Terlambat'
    elif current_time > end_limit:
        return jsonify({'success': False, 'message': 'Waktu absensi telah berakhir.'}), 400
        
    # 6. Simpan ke Database
    try:
        execute_db('''
            INSERT INTO attendance (student_id, date, time_in, status, scanned_by_id)
            VALUES (?, ?, ?, ?, ?)
        ''', [student_id, today, time_in, status, current_user.id])
        
        return jsonify({
            'success': True,
            'message': f'Absensi berhasil dicatat.',
            'status': status,
            'student': student
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Gagal menyimpan data: {str(e)}'}), 500

@attendance_bp.route('/history')
@login_required
@staff_required
def history():
    """Halaman riwayat absensi sederhana."""
    records = query_db('''
        SELECT a.date, a.time_in, a.status, s.nis, s.full_name, c.name as class_name
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        JOIN classes c ON s.class_id = c.id
        ORDER BY a.created_at DESC
        LIMIT 100
    ''')
    return render_template('attendance/history.html', records=records)