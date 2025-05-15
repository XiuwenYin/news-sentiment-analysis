# tests/conftest.py
import pytest
import time
from app import create_app, db
from config import TestConfig
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---------- 基础 Fixtures ----------

@pytest.fixture(scope='session')
def app():
    app = create_app(TestConfig)
    return app

@pytest.fixture(scope='function')
def test_client(app):
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

@pytest.fixture(scope='function')
def init_database(app):
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def new_user(app):
    from app.models import User
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        return user

# ---------- Selenium 登录测试用例 Fixture ----------

@pytest.fixture(scope="function")
def test_user_login(app, browser, init_database, live_server):
    from app.models import User

    app.config['DEBUG'] = True
    app.config['TESTING'] = True

    with app.app_context():
        db.create_all()
        user = User(username="test1", email="test1@email.com")
        user.set_password("test1")
        db.session.add(user)
        db.session.commit()

    browser.visit(live_server.url() + "/login")

    browser.fill("username", "test1")
    browser.fill("password", "test1")

    wait = WebDriverWait(browser.driver, 10)
    login_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"][value=\"Sign In\"]'))
    )
    browser.driver.execute_script("arguments[0].click();", login_button)

    wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Upload")))
    browser.find_link_by_text("Upload").first.click()
    wait.until(EC.presence_of_element_located((By.NAME, "post_title")))

    yield browser
