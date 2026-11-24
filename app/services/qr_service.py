import os
import uuid
import qrcode
from ..database import execute_db, query_db
from flask import current_app

def generate_token(student_id):
    """Membuat atau meregenerasi token UUID unik untuk siswa."""
    token = str(uuid.uuid4())
    
    existing = query_db("SELECT id FROM qr_tokens WHERE student_id = ?", [student_id], one=True)
    if existing:
        execute_db("UPDATE qr_tokens SET token = ?, is_active = 1, created_at = CURRENT_TIMESTAMP WHERE student_id = ?", 
                   [token, student_id])
    else:
        execute_db("INSERT INTO qr_tokens (student_id, token, is_active) VALUES (?, ?, 1)", 
                   [student_id, token])
    return token

def create_qr_image(token, nis):
    """Membuat gambar QR Code dari token dan menyimpannya ke folder static."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H, # High error correction
        box_size=10,
        border=2,
    )
    qr.add_data(token)
    qr.make(fit=True)
    
    # Menggunakan warna Deep Emerald (#064E3B) sesuai Design System
    img = qr.make_image(fill_color="#064E3B", back_color="white").convert('RGB')
    
    filename = f"qr_{nis}.png"
    upload_folder = os.path.join(current_app.root_path, 'static', 'qr_codes')
    os.makedirs(upload_folder, exist_ok=True)
    
    filepath = os.path.join(upload_folder, filename)
    img.save(filepath)
    
    return f"qr_codes/{filename}"