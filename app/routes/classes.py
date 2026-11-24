from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from ..utils.decorators import admin_required
from ..database import query_db, execute_db, get_db

classes_bp = Blueprint('classes', __name__, url_prefix='/classes', template_folder='../templates/classes')

@classes_bp.route('/')
@login_required
@admin_required
def index():
    classes = query_db('''
        SELECT c.*, u.full_name as wali_kelas, ay.name as tahun_ajaran,
        (SELECT COUNT(*) FROM students WHERE class_id = c.id AND status = 1) as jumlah_siswa
        FROM classes c
        LEFT JOIN users u ON c.homeroom_teacher_id = u.id
        JOIN academic_years ay ON c.academic_year_id = ay.id
        ORDER BY c.grade_level, c.name
    ''')
    # Ambil daftar guru untuk dropdown wali kelas
    teachers = query_db("SELECT id, full_name FROM users WHERE role IN ('admin', 'guru') AND status = 1")
    return render_template('classes/index.html', classes=classes, teachers=teachers)

@classes_bp.route('/add', methods=['POST'])
@login_required
@admin_required
def add():
    name = request.form.get('name')
    grade_level = request.form.get('grade_level')
    homeroom_teacher_id = request.form.get('homeroom_teacher_id') or None
    academic_year_id = request.form.get('academic_year_id')
    
    try:
        execute_db('''
            INSERT INTO classes (name, grade_level, homeroom_teacher_id, academic_year_id)
            VALUES (?, ?, ?, ?)
        ''', [name, grade_level, homeroom_teacher_id, academic_year_id])
        flash(f'Kelas {name} berhasil ditambahkan.', 'success')
    except Exception as e:
        flash(f'Gagal menambahkan kelas: {str(e)}', 'danger')
        
    return redirect(url_for('classes.index'))

@classes_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
@admin_required
def edit(id):
    name = request.form.get('name')
    grade_level = request.form.get('grade_level')
    homeroom_teacher_id = request.form.get('homeroom_teacher_id') or None
    
    try:
        execute_db('''
            UPDATE classes SET name = ?, grade_level = ?, homeroom_teacher_id = ?
            WHERE id = ?
        ''', [name, grade_level, homeroom_teacher_id, id])
        flash('Data kelas berhasil diperbarui.', 'success')
    except Exception as e:
        flash(f'Gagal memperbarui kelas: {str(e)}', 'danger')
        
    return redirect(url_for('classes.index'))

@classes_bp.route('/delete/<int:id>')
@login_required
@admin_required
def delete(id):
    try:
        execute_db('DELETE FROM classes WHERE id = ?', [id])
        flash('Kelas berhasil dihapus.', 'success')
    except Exception as e:
        flash('Gagal menghapus kelas. Pastikan tidak ada siswa di kelas ini.', 'danger')
    return redirect(url_for('classes.index'))