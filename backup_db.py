import os
import shutil
from datetime import datetime

def backup_database():
    # Path database utama
    db_path = os.path.join('instance', 'attendance.db')
    
    # Folder tujuan backup
    backup_dir = 'backups'
    os.makedirs(backup_dir, exist_ok=True)
    
    if not os.path.exists(db_path):
        print("❌ Database tidak ditemukan. Pastikan aplikasi sudah pernah dijalankan.")
        return

    # Format nama file backup: backup_YYYYMMDD_HHMMSS.db
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backup berhasil dibuat: {backup_path}")
    except Exception as e:
        print(f"❌ Gagal melakukan backup: {e}")

if __name__ == '__main__':
    print("🔄 Memulai proses backup database AL-KAUTSAR...")
    backup_database()