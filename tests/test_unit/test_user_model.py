# tests/test_unit/test_user_model.py
import pytest
from app.models import User
from app import db
from sqlalchemy.exc import IntegrityError 

@pytest.fixture(scope='function')
def persisted_user_id(app, init_database): 
    """Creates a user, saves it to the database, and returns its ID."""
    with app.app_context():
        user = User(username='test_persisted', email='persisted@example.com')
        user.set_password('a_strong_password')
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        return user_id # return ID

# --- Test User model ---

def test_new_user_creation(new_user): 
    """Test Plan 1.1.1: Unit Test - New User Creation"""
    assert new_user.username == 'testuser'
    assert new_user.email == 'test@example.com'
    assert new_user.password_hash is None
    # Assert profile_completed, expect the new_user fixture to handle default values ​​correctly
    # If you still have problems after modifying the new_user fixture in conftest.py, you can temporarily comment this line
    assert new_user.profile_completed is False, \
        f"Expected profile_completed to be False, but got {new_user.profile_completed}"

def test_set_password(new_user):
    """Test Plan 1.1.2 (Part): Password Settings"""
    new_user.set_password('cat')
    assert new_user.password_hash is not None
    assert new_user.password_hash != 'cat'

def test_check_password(new_user):
    """Test Plan 1.1.2 (Part): Password Authentication"""
    new_user.set_password('dog')
    assert new_user.check_password('dog') is True
    assert new_user.check_password('cat') is False

def test_password_hashes_are_random(new_user): # new_user is here just to get the User class
    """Test Plan 1.1.2 (Partial): Ensure the same password generates different hashes (with salt)"""
    # Create two separate user instances for comparison
    u1 = User(username='user1_rand', email='user1_rand@example.com')
    u1.set_password('commonpassword')

    u2 = User(username='user2_rand', email='user2_rand@example.com')
    u2.set_password('commonpassword')

    assert u1.password_hash is not None
    assert u2.password_hash is not None
    assert u1.password_hash != u2.password_hash

def test_user_representation(new_user):
    """Test Plan 1.1.3: User Model String Representation"""
    assert repr(new_user) == '<User testuser>'

def test_user_creation_in_db(app, init_database):
    """Test Plan 1.1.1 (partial): Test user creation and retrieval from database"""
    with app.app_context():
        u = User(username='dbuser', email='db@example.com', age=30, gender='male')
        u.set_password('securepass123')
        u.profile_completed = True 

        db.session.add(u)
        db.session.commit()

        # Use user_id to query to ensure that the latest persistent state is obtained
        retrieved_user = db.session.get(User, u.id)

        assert retrieved_user is not None
        assert retrieved_user.username == 'dbuser'
        assert retrieved_user.email == 'db@example.com'
        assert retrieved_user.check_password('securepass123')
        assert retrieved_user.age == 30
        assert retrieved_user.gender == 'male'
        assert retrieved_user.profile_completed is True

def test_username_uniqueness(app, init_database, persisted_user_id): 
    """Test Plan (implicit): Ensure uniqueness of username field"""
    with app.app_context():
        existing_user = db.session.get(User, persisted_user_id)
        assert existing_user is not None, "Persisted user not found in DB by ID"

        duplicate_user = User(username=existing_user.username, email='another@example.com')
        db.session.add(duplicate_user)
        with pytest.raises(IntegrityError): 
            db.session.commit()
        db.session.rollback() 

def test_email_uniqueness(app, init_database, persisted_user_id):
    """Test Plan (implicit): Ensuring uniqueness of email field"""
    with app.app_context():
        existing_user = db.session.get(User, persisted_user_id)
        assert existing_user is not None, "Persisted user not found in DB by ID"

        duplicate_email_user = User(username='anotheruser', email=existing_user.email)
        db.session.add(duplicate_email_user)
        with pytest.raises(IntegrityError): # 
            db.session.commit()
        db.session.rollback()

