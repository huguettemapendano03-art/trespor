# test_app.py
import unittest
import json
import os
from app import app
from models import init_db, get_db_connection

class TestBulletinApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_secret'
        self.client = app.test_client()
        init_db()

    def test_login_success(self):
        response = self.client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Syst\xc3\xa8me de Gestion des Bulletins', response.data)

    def test_api_bulletin_data(self):
        # Login first
        self.client.post('/login', data={'username': 'admin', 'password': 'admin123'})
        response = self.client.get('/api/student/1/bulletin')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('student', data)
        self.assertEqual(data['student']['full_name'], 'Trésor Mapendano')
        self.assertIn('grades', data)
        self.assertTrue(len(data['grades']) > 0)

    def test_grade_update_and_recalculation(self):
        self.client.post('/login', data={'username': 'admin', 'password': 'admin123'})

        # Update P1 for Subject 1 (Français) to 10.0
        update_res = self.client.post('/api/grade/update',
            data=json.dumps({'student_id': 1, 'subject_id': 1, 'field': 'p1', 'value': 10.0}),
            content_type='application/json'
        )
        self.assertEqual(update_res.status_code, 200)

        # Retrieve updated bulletin and check calculation
        get_res = self.client.get('/api/student/1/bulletin')
        data = json.loads(get_res.data)
        francais_grade = next(g for g in data['grades'] if g['subject_id'] == 1)
        self.assertEqual(francais_grade['p1'], 10.0)

    def test_pdf_download(self):
        self.client.post('/login', data={'username': 'admin', 'password': 'admin123'})
        response = self.client.get('/student/1/download-pdf')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/pdf')
        self.assertTrue(len(response.data) > 0)

if __name__ == '__main__':
    unittest.main()
