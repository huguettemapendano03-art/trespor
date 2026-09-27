# models.py
import sqlite3
import os

DB_PATH = 'bulletin_scolaire.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table des écoles
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT,
            logo_url TEXT
        )
    ''')

    # Table des utilisateurs (Direction / Enseignants)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL, -- 'ADMIN' ou 'TEACHER'
            subject_assigned TEXT -- Matière attribuée pour les enseignants (ex: 'Français')
        )
    ''')

    # Table des élèves
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_code TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            classroom TEXT NOT NULL,
            school_year TEXT NOT NULL
        )
    ''')

    # Table des matières
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            max_p1 REAL DEFAULT 10.0,
            max_p2 REAL DEFAULT 10.0,
            max_exam1 REAL DEFAULT 20.0,
            max_p3 REAL DEFAULT 10.0,
            max_p4 REAL DEFAULT 10.0,
            max_exam2 REAL DEFAULT 20.0
        )
    ''')

    # Table des cotes / notes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            p1 REAL DEFAULT 0,
            p2 REAL DEFAULT 0,
            exam1 REAL DEFAULT 0,
            p3 REAL DEFAULT 0,
            p4 REAL DEFAULT 0,
            exam2 REAL DEFAULT 0,
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (subject_id) REFERENCES subjects (id),
            UNIQUE(student_id, subject_id)
        )
    ''')

    # Insertion des données par défaut si vide
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password, full_name, role) VALUES ('admin', 'admin123', 'Direction Générale', 'ADMIN')")
        cursor.execute("INSERT INTO users (username, password, full_name, role, subject_assigned) VALUES ('prof_francais', 'prof123', 'M. Kabangu (Français)', 'TEACHER', 'Français')")
        cursor.execute("INSERT INTO users (username, password, full_name, role, subject_assigned) VALUES ('prof_math', 'prof123', 'Mme. Sarah (Mathématiques)', 'TEACHER', 'Mathématiques')")
        cursor.execute("INSERT INTO users (username, password, full_name, role, subject_assigned) VALUES ('prof_histoire', 'prof123', 'M. Mukendi (Histoire-Géo)', 'TEACHER', 'Histoire-Géo')")

    cursor.execute('SELECT COUNT(*) FROM students')
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO students (student_code, full_name, classroom, school_year) VALUES ('ELV-2025-001', 'Trésor Mapendano', '6ème Littéraire A', '2024-2025')")
        cursor.execute("INSERT INTO students (student_code, full_name, classroom, school_year) VALUES ('ELV-2025-002', 'Amani Marie', '6ème Littéraire A', '2024-2025')")

    cursor.execute('SELECT COUNT(*) FROM subjects')
    if cursor.fetchone()[0] == 0:
        subjects_data = [
            ('Français', 10, 10, 20, 10, 10, 20),
            ('Mathématiques', 10, 10, 20, 10, 10, 20),
            ('Histoire-Géo', 10, 10, 20, 10, 10, 20),
            ('Anglais', 10, 10, 20, 10, 10, 20),
            ('Physique-Chimie', 10, 10, 20, 10, 10, 20),
            ('Conduite & Éducation', 10, 10, 20, 10, 10, 20)
        ]
        for s in subjects_data:
            cursor.execute("INSERT INTO subjects (name, max_p1, max_p2, max_exam1, max_p3, max_p4, max_exam2) VALUES (?, ?, ?, ?, ?, ?, ?)", s)

    # Initialiser les cotes par défaut pour Trésor Mapendano
    cursor.execute("SELECT id FROM students WHERE student_code='ELV-2025-001'")
    student_id = cursor.fetchone()['id']

    cursor.execute("SELECT id, name FROM subjects")
    subjects = cursor.fetchall()

    for sub in subjects:
        cursor.execute("SELECT COUNT(*) FROM grades WHERE student_id=? AND subject_id=?", (student_id, sub['id']))
        if cursor.fetchone()[0] == 0:
            if sub['name'] == 'Français':
                cursor.execute("INSERT INTO grades (student_id, subject_id, p1, p2, exam1, p3, p4, exam2) VALUES (?, ?, 8.5, 9.0, 17.0, 8.0, 8.5, 16.0)", (student_id, sub['id']))
            elif sub['name'] == 'Mathématiques':
                cursor.execute("INSERT INTO grades (student_id, subject_id, p1, p2, exam1, p3, p4, exam2) VALUES (?, ?, 7.0, 8.0, 15.0, 7.5, 8.0, 14.5)", (student_id, sub['id']))
            else:
                cursor.execute("INSERT INTO grades (student_id, subject_id, p1, p2, exam1, p3, p4, exam2) VALUES (?, ?, 8.0, 8.5, 16.0, 8.0, 8.0, 15.0)", (student_id, sub['id']))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Base de données initialisée avec succès.")
