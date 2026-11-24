from flask_login import UserMixin

class User(UserMixin):
    """
    Model representasi Pengguna untuk Flask-Login.
    Mengambil data dari sqlite3.Row.
    """
    def __init__(self, id, username, full_name, role, status, password_hash=None):
        self.id = id
        self.username = username
        self.full_name = full_name
        self.role = role
        self.status = status
        self.password_hash = password_hash

    @property
    def is_active(self):
        """Override default is_active dari UserMixin"""
        return self.status == 1
        
    def __repr__(self):
        return f'<User {self.username}>'