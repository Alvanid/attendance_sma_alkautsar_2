from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from ..utils.decorators import staff_required
from ..database import query_db
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/')

@dashboard_bp.route('/')
@login_required
@staff_required
def index():
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 1. Statistik Utama
    total_students = query_db('SELECT COUNT(*) as count FROM students WHERE status = 1', one=True)['count']
    total_classes = query_db('SELECT COUNT(*) as count FROM classes', one=True)['count']
    
    # 2. Rekap Absensi Hari Ini
    att_today = query_db('''
        SELECT status, COUNT(*) as count 
        FROM attendance 
        WHERE date = ? 
        GROUP BY status
    ''', [today])
    
    att_dict = {row['status']: row['count'] for row in att_today}
    hadir = att_dict.get('Hadir', 0)
    terlambat = att_dict.get('Terlambat', 0)
    izin = att_dict.get('Izin', 0)
    sakit = att_dict.get('Sakit', 0)
    alpa = att_dict.get('Alpa', 0)
    
    total_hadir_bersih = hadir + terlambat
    
    # Perbaikan Indentasi: Pastikan baris ini menggunakan 4 spasi di awalnya
    persen_kehadiran = round((total_hadir_bersih / total_students * 100), 1) if total_students > 0 else 0
    
    # 3. Aktivitas Absensi Terbaru (Limit 5)
    recent_att = query_db('''
        SELECT a.time_in, a.status, s.full_name, c.name as class_name
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        JOIN classes c ON s.class_id = c.id
        ORDER BY a.created_at DESC
        LIMIT 5
    ''')
    
    return render_template('dashboard/index.html', 
                           total_students=total_students,
                           total_classes=total_classes,
                           hadir=hadir,
                           terlambat=terlambat,
                           izin=izin,
                           sakit=sakit,
                           alpa=alpa,
                           persen_kehadiran=persen_kehadiran,
                           recent_att=recent_att,
                           today=today)

@dashboard_bp.route('/api/chart-data')
@login_required
def chart_data():
    """Endpoint API untuk menyediakan data grafik mingguan."""
    labels = []
    data_hadir = []
    data_terlambat = []
    
    # Ambil data 7 hari terakhir
    for i in range(6, -1, -1):
        day = datetime.now() - timedelta(days=i)
        date_str = day.strftime('%Y-%m-%d')
        label = day.strftime('%d %b')
        labels.append(label)
        
        att = query_db('''
            SELECT status, COUNT(*) as count 
            FROM attendance 
            WHERE date = ? 
            GROUP BY status
        ''', [date_str])
        att_dict = {row['status']: row['count'] for row in att}
        
        data_hadir.append(att_dict.get('Hadir', 0))
        data_terlambat.append(att_dict.get('Terlambat', 0))
        
    return jsonify({
        'labels': labels,
        'datasets': [
            {'label': 'Hadir', 'data': data_hadir, 'backgroundColor': '#168568'},
            {'label': 'Terlambat', 'data': data_terlambat, 'backgroundColor': '#C5A46D'}
        ]
    })