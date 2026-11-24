from flask import Blueprint, render_template, request, send_file, current_app
from flask_login import login_required
from ..utils.decorators import staff_required
from ..database import query_db
from ..services.report_service import get_attendance_summary, generate_excel_report
from datetime import datetime, timedelta

reports_bp = Blueprint('reports', __name__, url_prefix='/reports', template_folder='../templates/reports')

@reports_bp.route('/')
@login_required
@staff_required
def index():
    # Default filter: 7 hari terakhir
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d')
    
    # Ambil filter dari URL params (jika ada)
    f_start = request.args.get('start_date', start_date)
    f_end = request.args.get('end_date', end_date)
    f_class = request.args.get('class_id', '')
    f_status = request.args.get('status', '')
    
    records = get_attendance_summary(f_start, f_end, f_class if f_class else None)
    
    # Filter status di Python (karena query SQL sudah jalan)
    if f_status:
        records = [r for r in records if r['status'] == f_status]
        
    # Hitung Statistik
    stats = {'Hadir': 0, 'Terlambat': 0, 'Izin': 0, 'Sakit': 0, 'Alpa': 0}
    for r in records:
        if r['status'] in stats:
            stats[r['status']] += 1
            
    total_records = len(records)
    total_hadir_bersih = stats['Hadir'] + stats['Terlambat']
    persen = round((total_hadir_bersih / total_records * 100), 1) if total_records > 0 else 0
    
    classes = query_db("SELECT id, name FROM classes ORDER BY name")
    
    return render_template('reports/index.html', 
                           records=records, 
                           stats=stats, 
                           total=total_records,
                           persen=persen,
                           classes=classes,
                           filters={'start': f_start, 'end': f_end, 'class': f_class, 'status': f_status})

@reports_bp.route('/export/excel')
@login_required
@staff_required
def export_excel():
    f_start = request.args.get('start_date')
    f_end = request.args.get('end_date')
    f_class = request.args.get('class_id')
    
    records = get_attendance_summary(f_start, f_end, f_class if f_class else None)
    excel_file = generate_excel_report(records, f_start, f_end)
    
    filename = f"Rekap_Absensi_{f_start}_sd_{f_end}.xlsx"
    return send_file(
        excel_file, 
        download_name=filename, 
        as_attachment=True, 
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )