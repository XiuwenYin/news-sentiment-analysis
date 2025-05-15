import unittest
from app import app, db
app.config.from_object('config.TestingConfig')
from app.models import User
from flask import url_for
from werkzeug.security import generate_password_hash

# 2.2.2 Unit Test - Test whether the GET route of the upload page is accessible
# This test class is used to verify whether the GET request of the upload page can be accessed normally and whether the page contains the upload form fields.
# ./venv/bin/python -m unittest discover -s app/tests/test_unit -p "test_upload_route.py"
class TestUploadRoute(unittest.TestCase):

    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        self.client = app.test_client()

        db.create_all()
        user = User.query.filter_by(username='testuser').first()
        if not user:
            user = User(username='testuser', email='test@example.com')
            user.set_password('testpass')
            db.session.add(user)
            db.session.commit()

        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass'
        }, follow_redirects=True)
        login_response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass'
        }, follow_redirects=True)
        
        # print("LOGIN RESPONSE HTML:")
        # print(login_response.get_data(as_text=True))

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_upload_get_route_status_code(self):
        response = self.client.get('/upload')
        self.assertEqual(response.status_code, 200)

    def test_upload_get_route_form_fields_present(self):
        response = self.client.get('/upload')
        data = response.get_data(as_text=True)
        self.assertIn('<form', data)
        self.assertIn('name="post_title"', data)
        self.assertIn('name="news_content"', data)

if __name__=='__main__':
    unittest.main()
