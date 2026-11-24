import sqlite3
import os
from flask import current_app, g

def get_db():
    """
    Mendapatkan koneksi database. 
    Menggunakan 'g' object untuk menyimpan koneksi per request.
    """
    if 'db' not in g:
        # Pastikan folder instance ada
        db_path = current_app.config['DATABASE'].replace('sqlite:///', '')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        g.db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Mengembalikan baris sebagai dictionary (row['column_name'])
        g.db.row_factory = sqlite3.Row
        
        # Mengaktifkan Foreign Key support di SQLite
        g.db.execute('PRAGMA foreign_keys = ON')
        
    return g.db

def close_db(e=None):
    """
    Menutup koneksi database di akhir request.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """
    Membaca schema.sql dan mengeksekusinya ke database.
    """
    db = get_db()
    with current_app.open_resource('schema.sql', mode='r') as f:
        db.executescript(f.read())

def query_db(query, args=(), one=False):
    """
    Helper function untuk eksekusi query SELECT.
    """
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    """
    Helper function untuk eksekusi query INSERT, UPDATE, DELETE.
    Menggunakan commit otomatis dan rollback jika terjadi error.
    """
    db = get_db()
    try:
        cur = db.execute(query, args)
        db.commit()
        return cur.lastrowid
    except sqlite3.Error as e:
        db.rollback()
        current_app.logger.error(f"Database Error: {e}")
        raise e