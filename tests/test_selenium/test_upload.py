import unittest
import time
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app import create_app, db
from app.models import User
from config import TestConfig as TestingConfig

BASE_URL = "http://127.0.0.1:5000"

class TestUploadNews(unittest.TestCase):
    DEFAULT_USERNAME = "test1"
    DEFAULT_PASSWORD = "test1"

    @classmethod
    def setUpClass(cls):
        # Set the test database path
        test_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tests', 'test_app.db')
        full_path = os.path.abspath(test_db_path)
        print("SQLite route:", full_path)

        # Create database directory (if it does not exist)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Dynamically modify database URI without modifying the config. py ontology
        TestingConfig.SQLALCHEMY_DATABASE_URI = f"sqlite:///{full_path}"

        # Initialize Flask app and database
        cls.app = create_app(TestingConfig)
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()

        # Create default user test1
        if not User.query.filter_by(username="test1").first():
            user = User(
                username="test1",
                email="test1@example.com",
                profile_completed=True
            )
            user.set_password("test1")
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

        # Log in as test1 user
        self.driver.get(f"{BASE_URL}/auth/login")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        ).send_keys(self.DEFAULT_USERNAME)

        self.driver.find_element(By.NAME, "password").send_keys(self.DEFAULT_PASSWORD)
        login_btn = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
        self.driver.execute_script("arguments[0].click();", login_btn)
        time.sleep(1)

    def tearDown(self):
        self.driver.quit()

    def test_news_upload_and_analysis(self):
        """Test the ability to correctly display results after uploading news and conducting sentiment analysis"""
        driver = self.driver
        wait = WebDriverWait(driver, 10)

        # To upload page
        driver.get(BASE_URL + "/upload/upload")
        time.sleep(1)

        # Current URL
        print("Current UPL:", driver.current_url)

        #Print the first 300 characters of the page source code
        print("Page source code:", driver.page_source[:300])

        # Waiting for form fields to load
        post_title_input = wait.until(EC.presence_of_element_located((By.NAME, "post_title")))
        news_content_input = wait.until(EC.presence_of_element_located((By.NAME, "news_content")))

        # Submit Form
        post_title_input.send_keys("Test News Title")
        sample_news = (
            "Researchers have developed a new AI model that achieves state-of-the-art performance "
            "on several benchmark datasets. Experts believe this could revolutionize fields such as "
            "healthcare, finance, and education."
        )
        news_content_input.send_keys(sample_news)

        # Submit Form
        submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']")))
        driver.execute_script("arguments[0].click();", submit_button)

        # Check if the analysis results appear
        wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Result')]")))
        self.assertIn("Result", driver.page_source)
        self.assertRegex(driver.page_source, r"(?i)Category\s*:")   # 包含分类信息
        self.assertRegex(driver.page_source, r"(?i)Summary\s*:")    # 包含摘要信息
        self.assertRegex(driver.page_source, r"(?i)Emotion[s]?\s*:")  # 包含情绪信息

if __name__ == "__main__":
    unittest.main()
