# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file
import sqlite3
from models import init_db, get_db_connection
from pdf_generator import generate_bulletin_pdf

app = Flask(__name__)
app.secret_key = 'bulletin_secret_key_pro'

# Initialiser la base de données au lancement
init_db()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['role'] = user['role']
            session['subject_assigned'] = user['subject_assigned']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Identifiants incorrects.")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    subjects = conn.execute('SELECT * FROM subjects').fetchall()
    conn.close()

    return render_template('dashboard.html', students=students, subjects=subjects, user=session)

@app.route('/api/student/<int:student_id>/bulletin')
def get_student_bulletin(student_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Non autorisé'}), 401

    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()

    if not student:
        conn.close()
        return jsonify({'error': 'Élève non trouvé'}), 404

    query = '''
        SELECT s.id as subject_id, s.name as subject_name,
               g.p1, g.p2, g.exam1, g.p3, g.p4, g.exam2
        FROM subjects s
        LEFT JOIN grades g ON s.id = g.subject_id AND g.student_id = ?
    '''
    rows = conn.execute(query, (student_id,)).fetchall()
    conn.close()

    grades = []
    total_obtained = 0
    total_max = 0

    for r in rows:
        p1 = r['p1'] if r['p1'] is not None else 0
        p2 = r['p2'] if r['p2'] is not None else 0
        exam1 = r['exam1'] if r['exam1'] is not None else 0
        p3 = r['p3'] if r['p3'] is not None else 0
        p4 = r['p4'] if r['p4'] is not None else 0
        exam2 = r['exam2'] if r['exam2'] is not None else 0

        tot_s1 = p1 + p2 + exam1
        tot_s2 = p3 + p4 + exam2
        tot_an = tot_s1 + tot_s2

        total_obtained += tot_an
        total_max += 80

        grades.append({
            'subject_id': r['subject_id'],
            'subject_name': r['subject_name'],
            'p1': p1, 'p2': p2, 'exam1': exam1, 'tot_s1': tot_s1,
            'p3': p3, 'p4': p4, 'exam2': exam2, 'tot_s2': tot_s2,
            'tot_an': tot_an
        })

    percentage = round((total_obtained / total_max * 100), 2) if total_max > 0 else 0

    return jsonify({
        'student': dict(student),
        'grades': grades,
        'total_obtained': total_obtained,
        'total_max': total_max,
        'percentage': percentage
    })

@app.route('/api/grade/update', methods=['POST'])
def update_grade():
    if 'user_id' not in session:
        return jsonify({'error': 'Non autorisé'}), 401

    data = request.json
    student_id = data.get('student_id')
    subject_id = data.get('subject_id')
    field = data.get('field') # 'p1', 'p2', 'exam1', 'p3', 'p4', 'exam2'
    value = float(data.get('value', 0))

    valid_fields = ['p1', 'p2', 'exam1', 'p3', 'p4', 'exam2']
    if field not in valid_fields:
        return jsonify({'error': 'Champ invalide'}), 400

    conn = get_db_connection()

    # Vérifier l'existence de la ligne dans grades
    existing = conn.execute('SELECT id FROM grades WHERE student_id = ? AND subject_id = ?', (student_id, subject_id)).fetchone()

    if existing:
        conn.execute(f'UPDATE grades SET {field} = ? WHERE student_id = ? AND subject_id = ?', (value, student_id, subject_id))
    else:
        conn.execute(f'INSERT INTO grades (student_id, subject_id, {field}) VALUES (?, ?, ?)', (student_id, subject_id, value))

    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Note mise à jour'})

@app.route('/student/<int:student_id>/download-pdf')
def download_pdf(student_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()

    if not student:
        conn.close()
        return "Élève introuvable", 404

    query = '''
        SELECT s.name as subject_name,
               COALESCE(g.p1, 0) as p1, COALESCE(g.p2, 0) as p2, COALESCE(g.exam1, 0) as exam1,
               COALESCE(g.p3, 0) as p3, COALESCE(g.p4, 0) as p4, COALESCE(g.exam2, 0) as exam2
        FROM subjects s
        LEFT JOIN grades g ON s.id = g.subject_id AND g.student_id = ?
    '''
    grades = conn.execute(query, (student_id,)).fetchall()
    conn.close()

    pdf_buffer = generate_bulletin_pdf(dict(student), [dict(g) for g in grades])

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"Bulletin_{student['full_name'].replace(' ', '_')}.pdf",
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
