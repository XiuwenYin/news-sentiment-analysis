# tests/test_unit/test_forms.py
import pytest
from app.forms import LoginForm, RegistrationForm
from app.models import User
from app import db as app_db

class TestLoginForm:
    def test_login_form_valid_data(self, app):
        with app.app_context():
            form_data = {
                'username': 'testuser',
                'password': 'password123',
                'remember_me': True
            }
            form = LoginForm(**form_data)
            assert form.validate() is True
            assert not form.errors

    def test_login_form_missing_username(self, app):
        with app.app_context():
            form = LoginForm(password='password123')
            assert form.validate() is False
            assert 'username' in form.errors
            assert 'This field is required.' in form.errors['username']

    def test_login_form_missing_password(self, app):
        with app.app_context():
            form = LoginForm(username='testuser')
            assert form.validate() is False
            assert 'password' in form.errors
            assert 'This field is required.' in form.errors['password']

    def test_login_form_empty_data(self, app):
        with app.app_context():
            form = LoginForm()
            assert form.validate() is False
            assert 'username' in form.errors
            assert 'password' in form.errors

    def test_login_form_remember_me_optional(self, app):
        with app.app_context():
            form1 = LoginForm(username='testuser', password='password123')
            assert form1.validate() is True
            assert form1.remember_me.data is False

            form2 = LoginForm(username='testuser', password='password123', remember_me=True)
            assert form2.validate() is True
            assert form2.remember_me.data is True

            form3 = LoginForm(username='testuser', password='password123', remember_me=False)
            assert form3.validate() is True
            assert form3.remember_me.data is False


class TestRegistrationForm:
    def test_registration_form_valid_data(self, app, init_database):
        with app.app_context():
            form_data = {
                'username': 'newuser',
                'email': 'new@example.com',
                'password': 'SecurePassword123!',
                'password2': 'SecurePassword123!'
            }
            form = RegistrationForm(**form_data)
            assert form.validate() is True, f"Validation failed with errors: {form.errors}"
            assert not form.errors

    def test_registration_form_missing_fields(self, app, init_database):
        with app.app_context():
            form_empty = RegistrationForm()
            assert form_empty.validate() is False
            assert 'username' in form_empty.errors
            assert 'email' in form_empty.errors
            assert 'password' in form_empty.errors
            assert 'password2' in form_empty.errors

            form_no_email = RegistrationForm(username='u', password='p', password2='p')
            assert form_no_email.validate() is False
            assert 'email' in form_no_email.errors

    def test_registration_form_invalid_email(self, app, init_database):
        with app.app_context():
            form_data = {
                'username': 'newuser_invalid_email',
                'email': 'not-an-email',
                'password': 'SecurePassword123!',
                'password2': 'SecurePassword123!'
            }
            form = RegistrationForm(**form_data)
            assert form.validate() is False
            assert 'email' in form.errors
            assert any('Invalid email address' in error for error in form.errors['email'])

    def test_registration_form_password_mismatch(self, app, init_database):
        with app.app_context():
            form_data = {
                'username': 'newuser_pwd_mismatch',
                'email': 'new_mismatch@example.com',
                'password': 'SecurePassword123!',
                'password2': 'DifferentPassword!'
            }
            form = RegistrationForm(**form_data)
            assert form.validate() is False
            assert 'password2' in form.errors
            assert any('Passwords must match' in error for error in form.errors['password2']) or \
                   any('Field must be equal to' in error for error in form.errors['password2'])

    def test_registration_form_username_taken(self, app, init_database):
        with app.app_context():
            existing_user = User(username='existinguser', email='unique@example.com')
            existing_user.set_password('password')
            app_db.session.add(existing_user)
            app_db.session.commit()

            form_data = {
                'username': 'existinguser',
                'email': 'another@example.com',
                'password': 'SecurePassword123!',
                'password2': 'SecurePassword123!'
            }
            form = RegistrationForm(**form_data)
            assert form.validate() is False
            assert 'username' in form.errors
            assert 'Please use a different username.' in form.errors['username']

    def test_registration_form_email_taken(self, app, init_database):
        with app.app_context():
            existing_user = User(username='anotheruser', email='existing@example.com')
            existing_user.set_password('password')
            app_db.session.add(existing_user)
            app_db.session.commit()

            form_data = {
                'username': 'newusername_email_taken',
                'email': 'existing@example.com',
                'password': 'SecurePassword123!',
                'password2': 'SecurePassword123!'
            }
            form = RegistrationForm(**form_data)
            assert form.validate() is False
            assert 'email' in form.errors
            assert 'Please use a different email address.' in form.errors['email']

    def test_registration_form_username_and_email_available(self, app, init_database):
        with app.app_context():
            form_data = {
                'username': 'available_user',
                'email': 'available_email@example.com',
                'password': 'SecurePassword123!',
                'password2': 'SecurePassword123!'
            }
            form = RegistrationForm(**form_data)
            assert form.validate() is True, f"Validation failed: {form.errors}"
            assert 'username' not in form.errors
            assert 'email' not in form.errors