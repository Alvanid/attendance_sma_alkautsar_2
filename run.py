# Pastikan nama 'app' di bawah ini sesuai dengan nama folder 
# tempat file __init__.py (kode yang Anda kirimkan tadi) berada.
# Jika foldernya bernama 'app', biarkan seperti ini.
from app import create_app 

# Membuat instance aplikasi dengan konfigurasi 'default'
app = create_app('default')

if __name__ == '__main__':
    # Menjalankan server dalam mode debug
    app.run(debug=True, host='127.0.0.1', port=5000)