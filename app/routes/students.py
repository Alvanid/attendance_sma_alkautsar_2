import os
import io
import pandas as pd
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app
from flask_login import login_required
from ..utils.decorators import admin_required
from ..database import query_db, execute_db, get_db
from ..services.qr_service import generate_token, create_qr_image

students_bp = Blueprint('students', __name__, url_prefix='/students', template_folder='../templates/students')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@students_bp.route('/')
@login_required
@admin_required
def index():
    # Optimasi Query: Hanya ambil kolom yang ditampilkan di tabel
    students = query_db('''
        SELECT s.id, s.nis, s.full_name, s.gender, s.phone, c.name as class_name 
        FROM students s
        LEFT JOIN classes c ON s.class_id = c.id
        WHERE s.status = 1
        ORDER BY s.full_name
    ''')
    classes = query_db("SELECT id, name FROM classes ORDER BY name")
    return render_template('students/index.html', students=students, classes=classes)

@students_bp.route('/add', methods=['POST'])
@login_required
@admin_required
def add():
    nis = request.form.get('nis')
    nisn = request.form.get('nisn')
    full_name = request.form.get('full_name')
    gender = request.form.get('gender')
    birth_place = request.form.get('birth_place')
    birth_date = request.form.get('birth_date')
    address = request.form.get('address')
    phone = request.form.get('phone')
    class_id = request.form.get('class_id')
    
    # Handle Photo Upload
    photo_filename = None
    if 'photo' in request.files:
        file = request.files['photo']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(f"{nis}_{file.filename}")
            upload_folder = os.path.join(current_app.root_path, 'static', 'images', 'students')
            os.makedirs(upload_folder, exist_ok=True)
            file.save(os.path.join(upload_folder, filename))
            photo_filename = f"images/students/{filename}"

    # Get active academic year
    ay = query_db("SELECT id FROM academic_years WHERE is_active = 1", one=True)
    ay_id = ay['id'] if ay else 1

    try:
        student_id = execute_db('''
            INSERT INTO students (nis, nisn, full_name, gender, birth_place, birth_date, address, phone, photo, class_id, academic_year_id, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        ''', [nis, nisn, full_name, gender, birth_place, birth_date, address, phone, photo_filename, class_id, ay_id])
        
        # --- AUTO GENERATE QR CODE ---
        token = generate_token(student_id)
        create_qr_image(token, nis)
        # --------------------------------
        
        flash(f'Siswa {full_name} berhasil ditambahkan dan QR Code telah dibuat.', 'success')
    except Exception as e:
        flash(f'Gagal menambahkan siswa (NIS mungkin sudah terdaftar): {str(e)}', 'danger')
        
    return redirect(url_for('students.index'))

@students_bp.route('/delete/<int:id>')
@login_required
@admin_required
def delete(id):
    try:
        execute_db('UPDATE students SET status = 0 WHERE id = ?', [id]) # Soft delete
        flash('Siswa berhasil dinonaktifkan.', 'success')
    except Exception as e:
        flash('Gagal menghapus siswa.', 'danger')
    return redirect(url_for('students.index'))

@students_bp.route('/export')
@login_required
@admin_required
def export_excel():
    students = query_db('''
        SELECT s.nis, s.nisn, s.full_name, s.gender, s.birth_place, s.birth_date, 
               s.address, s.phone, c.name as kelas
        FROM students s
        JOIN classes c ON s.class_id = c.id
        WHERE s.status = 1
    ''')
    
    df = pd.DataFrame(students)
    df.columns = ['NIS', 'NISN', 'Nama Lengkap', 'Jenis Kelamin', 'Tempat Lahir', 
                  'Tanggal Lahir', 'Alamat', 'No Telepon', 'Kelas']
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data Siswa')
        
    output.seek(0)
    return send_file(output, download_name='Data_Siswa_AlKautsar.xlsx', as_attachment=True, 
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@students_bp.route('/import', methods=['POST'])
@login_required
@admin_required
def import_excel():
    if 'file' not in request.files:
        flash('Tidak ada file yang diunggah.', 'danger')
        return redirect(url_for('students.index'))
        
    file = request.files['file']
    if file and file.filename.endswith('.xlsx'):
        try:
            df = pd.read_excel(file)
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            success_count = 0
            error_count = 0
            db = get_db()
            
            ay = query_db("SELECT id FROM academic_years WHERE is_active = 1", one=True)
            ay_id = ay['id'] if ay else 1
            
            for index, row in df.iterrows():
                # --- PERBAIKAN SYNTAX (pd.notna) ---
                nis = str(row.get('nis', '')).strip() if pd.notna(row.get('nis')) else ''
                nama = str(row.get('nama lengkap', '')).strip() if pd.notna(row.get('nama lengkap')) else ''
                kelas_name = str(row.get('kelas', '')).strip() if pd.notna(row.get('kelas')) else ''
                jk = str(row.get('jenis kelamin', 'L')).strip().upper() if pd.notna(row.get('jenis kelamin')) else 'L'
                # -----------------------------------
                
                if not nis or not nama or not kelas_name:
                    error_count += 1
                    continue
                    
                kelas = query_db("SELECT id FROM classes WHERE name = ?", [kelas_name], one=True)
                if not kelas:
                    error_count += 1
                    continue
                    
                try:
                    cursor = db.execute('''
                        INSERT INTO students (nis, full_name, gender, class_id, academic_year_id, status)
                        VALUES (?, ?, ?, ?, ?, 1)
                    ''', (nis, nama, jk if jk in ['L', 'P'] else 'L', kelas['id'], ay_id))
                    
                    new_student_id = cursor.lastrowid
                    
                    # --- AUTO GENERATE QR CODE UNTUK IMPORT ---
                    token = generate_token(new_student_id)
                    create_qr_image(token, nis)
                    # ------------------------------------------
                    
                    success_count += 1
                except Exception:
                    error_count += 1
                    
            db.commit()
            flash(f'Import selesai: {success_count} berhasil, {error_count} gagal (duplikat/kelas tidak ditemukan).', 'info')
        except Exception as e:
            flash(f'Gagal membaca file Excel: {str(e)}', 'danger')
    else:
        flash('Format file harus .xlsx', 'danger')
        
    return redirect(url_for('students.index'))