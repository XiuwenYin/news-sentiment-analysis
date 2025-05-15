# tests/conftest.py
import pytest
from app import create_app, db # 假设你的 app/__init__.py 中有 create_app 和 db
from config import TestConfig # 从你的 config.py 导入 TestConfig

@pytest.fixture(scope='session') # 'session' scope means this runs once per test session
def app():
    """Create and configure a new app instance for each test session."""
    app = create_app(TestConfig) # 使用测试配置创建应用
    return app

@pytest.fixture(scope='function') # 'function' scope means this runs for each test function
def test_client(app):
    """A test client for the app."""
    with app.test_client() as client:
        with app.app_context(): # Push an application context
            db.create_all() # Create all database tables for in-memory db
        yield client # This is where the testing happens
        with app.app_context():
            db.drop_all() # Clean up by dropping all tables after test

@pytest.fixture(scope='function')
def init_database(app):
    """Initialize the database for tests that need pre-existing data."""
    with app.app_context():
        db.create_all()
        # You can add some initial data here if needed for many tests
        # For example:
        # user = User(username='testuser', email='test@example.com')
        # user.set_password('password')
        # db.session.add(user)
        # db.session.commit()
        yield db # Make the db instance available to the test
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def new_user(app): # Example fixture to create a user model instance
    from app.models import User
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        return user