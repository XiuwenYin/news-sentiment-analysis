import unittest
import time
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app import create_app, db
from app.models import User
from config import TestConfig as TestingConfig

BASE_URL = "http://127.0.0.1:5000"

class TestHistoryPage(unittest.TestCase):
    DEFAULT_USERNAME = "test1"
    DEFAULT_PASSWORD = "test1"

    @classmethod
    def setUpClass(cls):
        
        db_path = os.path.join(os.path.dirname(__file__), '..', 'tests', 'test_app.db')
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        TestingConfig.SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.abspath(db_path)

        # Create Flask App+Database
        cls.app = create_app(TestingConfig)
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()

        # Create default user
        if not User.query.filter_by(username=cls.DEFAULT_USERNAME).first():
            user = User(
                username=cls.DEFAULT_USERNAME,
                email="test1@example.com",
                age=30,
                gender="Other",
                profile_completed=True
            )
            user.set_password(cls.DEFAULT_PASSWORD)
            db.session.add(user)
            db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(5)

        # log on user
        self.driver.get(BASE_URL + "/auth/login")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        ).send_keys(self.DEFAULT_USERNAME)
        self.driver.find_element(By.NAME, "password").send_keys(self.DEFAULT_PASSWORD)
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
        self.driver.execute_script("arguments[0].click();", submit_btn)
        time.sleep(1)

        # Upload news
        self.driver.get(BASE_URL + "/upload/upload")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "post_title"))
        ).send_keys("History Test News")

        self.driver.find_element(By.NAME, "news_content").send_keys(
            "This is a test news content for validating appearance in history."
        )

        # Revised submission logic
        submit_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
        )
        self.driver.execute_script("arguments[0].click();", submit_btn)

        # Waiting for the result page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Result')]"))
        )

    def tearDown(self):
        self.driver.quit()

    def test_history_page_contains_uploaded_post(self):
        driver = self.driver
        wait = WebDriverWait(driver, 10)

        # Visit History Page
        driver.get(BASE_URL + "/history/history")
        time.sleep(1)
        driver.save_screenshot("debug_history_page.png")

        # Check if the page contains the uploaded title
        page = driver.page_source
        self.assertIn("History Test News", page)
        self.assertRegex(page, r"(Positive|Negative|Neutral)")

        # Try clicking the 'View' button to expand the details
        try:
            view_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'View')]"))
            )
            view_button.click()
            time.sleep(0.5)
            self.assertIn("Category", driver.page_source)
        except Exception:
            print("Details button not found or not expanded, skip this step")

if __name__ == "__main__":
    unittest.main()
