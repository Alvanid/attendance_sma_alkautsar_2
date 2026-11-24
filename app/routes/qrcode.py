import os
from flask import Blueprint, render_template, redirect, url_for, flash, send_from_directory, current_app
from flask_login import login_required
from ..utils.decorators import admin_required
from ..database import query_db, execute_db
from ..services.qr_service import generate_token, create_qr_image

qrcode_bp = Blueprint('qrcode', __name__, url_prefix='/qrcode', template_folder='../templates/qrcode')

@qrcode_bp.route('/generate/<int:student_id>')
@login_required
@admin_required
def generate(student_id):
    """Generate atau Regenerate QR Code untuk 1 siswa."""
    student = query_db("SELECT * FROM students WHERE id = ?", [student_id], one=True)
    if not student:
        flash('Siswa tidak ditemukan.', 'danger')
        return redirect(url_for('students.index'))
        
    token = generate_token(student_id)
    create_qr_image(token, student['nis'])
    
    flash(f'QR Code untuk {student["full_name"]} berhasil di-generate ulang!', 'success')
    return redirect(url_for('qrcode.card', student_id=student_id))

@qrcode_bp.route('/card/<int:student_id>')
@login_required
def card(student_id):
    """Halaman Preview dan Cetak Kartu Pelajar."""
    student = query_db('''
        SELECT s.*, c.name as class_name, ay.name as academic_year 
        FROM students s
        JOIN classes c ON s.class_id = c.id
        JOIN academic_years ay ON s.academic_year_id = ay.id
        WHERE s.id = ?
    ''', [student_id], one=True)
    
    if not student:
        flash('Siswa tidak ditemukan.', 'danger')
        return redirect(url_for('students.index'))
        
    qr_token = query_db("SELECT token FROM qr_tokens WHERE student_id = ? AND is_active = 1", [student_id], one=True)
    if not qr_token:
        flash('QR Code belum di-generate. Silakan generate terlebih dahulu.', 'warning')
        return redirect(url_for('students.index'))
        
    qr_filename = f"qr_{student['nis']}.png"
    qr_exists = os.path.exists(os.path.join(current_app.root_path, 'static', 'qr_codes', qr_filename))
    
    return render_template('qrcode/card.html', student=student, qr_exists=qr_exists, qr_filename=qr_filename)

@qrcode_bp.route('/download/<string:filename>')
@login_required
def download(filename):
    """Download file gambar QR Code (PNG)."""
    return send_from_directory(
        os.path.join(current_app.root_path, 'static', 'qr_codes'), 
        filename, 
        as_attachment=True
    )

@qrcode_bp.route('/batch/<int:class_id>')
@login_required
@admin_required
def batch_generate(class_id):
    """Generate QR Code massal untuk seluruh siswa di satu kelas."""
    students = query_db("SELECT id, nis FROM students WHERE class_id = ? AND status = 1", [class_id])
    count = 0
    for s in students:
        token = generate_token(s['id'])
        create_qr_image(token, s['nis'])
        count += 1
        
    flash(f'Berhasil generate {count} QR Code untuk kelas ini.', 'success')
    return redirect(url_for('students.index'))