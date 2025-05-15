# tests/conftest.py
import pytest
import os
import time
from app import create_app, db as flask_db
from config import TestConfig
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

@pytest.fixture(scope='session')
def app():
    app_instance = create_app(TestConfig)
    
    db_uri = app_instance.config['SQLALCHEMY_DATABASE_URI']
    db_file_path = None
    if db_uri.startswith('sqlite:///'):
        path_part = db_uri.replace('sqlite:///', '', 1)
        project_root_for_db = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if not os.path.isabs(path_part):
            db_file_path = os.path.join(project_root_for_db, path_part)
        else:
            db_file_path = path_part
            
    if db_file_path and os.path.exists(db_file_path):
        print(f"CONFLOG: Removing existing test database: {db_file_path}")
        try:
            os.remove(db_file_path)
        except OSError as e:
            print(f"CONFLOG: Error removing database file {db_file_path}: {e}")
            
    if db_file_path:
        db_dir = os.path.dirname(db_file_path)
        if db_dir and not os.path.exists(db_dir):
            print(f"CONFLOG: Creating directory for test database: {db_dir}")
            try:
                os.makedirs(db_dir)
            except OSError as e:
                 print(f"CONFLOG: Error creating directory {db_dir}: {e}")

    with app_instance.app_context():
        print(f"CONFLOG: Creating all tables for: {app_instance.config['SQLALCHEMY_DATABASE_URI']}")
        flask_db.create_all()
    
    yield app_instance
    
    with app_instance.app_context():
        print(f"CONFLOG: Dropping all tables for: {app_instance.config['SQLALCHEMY_DATABASE_URI']}")
        flask_db.drop_all() 
    
    if db_file_path and os.path.exists(db_file_path):
        print(f"CONFLOG: Removing test database file: {db_file_path}")
        try:
            os.remove(db_file_path)
        except OSError as e:
            print(f"CONFLOG: Error removing database file {db_file_path} on teardown: {e}")
        
        db_dir_final = os.path.dirname(db_file_path)
        if db_dir_final and os.path.exists(db_dir_final) and not os.listdir(db_dir_final):
            try:
                os.rmdir(db_dir_final)
                print(f"CONFLOG: Removed empty test database directory: {db_dir_final}")
            except OSError as e:
                print(f"CONFLOG: Could not remove directory {db_dir_final}: {e}")

@pytest.fixture(scope='function')
def test_client(app):
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='function')
def init_database(app):
    with app.app_context():
        flask_db.drop_all()
        flask_db.create_all()
    yield flask_db
    with app.app_context():
        flask_db.session.remove()

@pytest.fixture(scope='function')
def new_user(app):
    from app.models import User
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        model_default_for_profile_completed = None
        column_property = getattr(User, 'profile_completed', None)
        if column_property is not None and hasattr(column_property, 'property'):
            column_definition = column_property.property.columns[0]
            if hasattr(column_definition, 'default') and column_definition.default is not None:
                default_arg = column_definition.default.arg
                if callable(default_arg):
                    try: model_default_for_profile_completed = default_arg(None)
                    except TypeError: pass
                else: model_default_for_profile_completed = default_arg
        if user.profile_completed is None and model_default_for_profile_completed is False:
            user.profile_completed = False
        return user

@pytest.fixture(scope="session")
def _browser_instance(): # 移除了 live_server_host_port，因为 live_server 是 function scope
    print(f"CONFLOG: Initializing new browser instance for the session.")
    chrome_options = ChromeOptions()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    try:
        driver = webdriver.Chrome(options=chrome_options)
    except Exception as e:
        pytest.skip(f"Could not start ChromeDriver: {e}.")
    driver.implicitly_wait(10)
    yield driver
    print(f"CONFLOG: Quitting browser instance for the session.")
    driver.quit()

@pytest.fixture(scope="function")
def browser(_browser_instance, live_server): # live_server 是 function scope
    driver = _browser_instance
    print(f"CONFLOG_BROWSER_FUNC: Preparing browser. Clearing cookies. live_server at {live_server.url()}")
    driver.delete_all_cookies()
    # 导航到一个已知的基础状态页，例如应用的根，或者 about:blank
    # driver.get("about:blank") # 可选的额外重置步骤
    # driver.get(live_server.url()) # 确保在导航前 live_server 已启动
    return driver