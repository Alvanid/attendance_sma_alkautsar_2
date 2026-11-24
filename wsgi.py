from app import create_app

# Buat instance aplikasi dengan konfigurasi default/production
app = create_app('default')

if __name__ == "__main__":
    app.run()