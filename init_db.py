import sqlite3
import os
import sys
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def init_and_seed():
    db_path = os.path.join('instance', 'attendance.db')
    os.makedirs('instance', exist_ok=True)
    
    # Hapus database lama jika ada (Hati-hati: ini menghapus semua data!)
    if os.path.exists(db_path):
        print("⚠️  Database lama ditemukan. Menghapus untuk inisialisasi ulang...")
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    conn.execute('PRAGMA foreign_keys = ON')
    
    try:
        # 1. Load dan Eksekusi Schema
        schema_path = os.path.join('app', 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        print("✅ Skema database berhasil dibuat.")
        
        cursor = conn.cursor()
        
        # 2. Seed Super Admin
        # Password default: admin123
        admin_password = generate_password_hash('admin123')
        cursor.execute("""
            INSERT INTO users (username, password_hash, full_name, role, status) 
            VALUES (?, ?, ?, ?, ?)
        """, ('superadmin', admin_password, 'Super Administrator', 'super_admin', 1))
        print("👤 Super Admin dibuat (Username: superadmin | Password: admin123)")
        
        # 3. Seed Tahun Ajaran Aktif
        cursor.execute("""
            INSERT INTO academic_years (name, start_date, end_date, is_active)
            VALUES (?, ?, ?, ?)
        """, ('2025/2026', '2025-07-01', '2026-06-30', 1))
        ay_id = cursor.lastrowid
        print("📅 Tahun Ajaran 2025/2026 dibuat dan diaktifkan.")
        
        # 4. Seed Pengaturan Sekolah (School Settings)
        settings = [
            ('school_name', 'SMA AL-KAUTSAR MANYAR', 'Nama Sekolah'),
            ('school_address', 'Jl. Raya Sekaran, Lamongan', 'Alamat Sekolah'),
            ('attendance_start', '06:30', 'Jam Mulai Absensi'),
            ('attendance_on_time', '07:00', 'Batas Waktu Tepat Waktu'),
            ('attendance_end', '08:00', 'Jam Akhir Absensi'),
            ('timezone', 'Asia/Jakarta', 'Zona Waktu')
        ]
        cursor.executemany("INSERT INTO school_settings (key, value, description) VALUES (?, ?, ?)", settings)
        print("⚙️  Pengaturan sekolah default berhasil disimpan.")
        
        # 5. Seed Dummy Class (Kelas Contoh)
        cursor.execute("""
            INSERT INTO classes (name, grade_level, academic_year_id) VALUES (?, ?, ?)
        """, ('X-A', 'X', ay_id))
        print("🏫 Kelas contoh 'X-A' berhasil dibuat.")
        
        conn.commit()
        print("\n🎉 INISIALISASI DATABASE BERHASIL!")
        print("Anda sekarang dapat menjalankan aplikasi dengan: python run.py")
        
    except sqlite3.Error as e:
        print(f"❌ Terjadi kesalahan database: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == '__main__':
    init_and_seed()