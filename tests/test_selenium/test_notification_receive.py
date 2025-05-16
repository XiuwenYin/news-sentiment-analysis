import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests.test_selenium.test_auth_flows import robust_click

def test_notification_receive_flow(browser, live_server, user_with_notification, app):
    driver = browser
    base_url = live_server.url()
    username = user_with_notification["username"]
    password = user_with_notification["password"]
    notif_message = user_with_notification["notif_message"]

    # Log in as the user who was shared with
    driver.get(base_url + "/auth/login")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    ).send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    robust_click(driver, (By.CSS_SELECTOR, "button[type='submit'],input[type='submit']"))
    WebDriverWait(driver, 10).until(
        EC.url_contains("/index") or EC.url_matches(r"/$")
    )

    # Go to notifications page and check for notification
    driver.get(base_url + "/notifications/notifications")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "notification-message"))
    )
    notif_texts = [el.text for el in driver.find_elements(By.CLASS_NAME, "notification-message")]
    assert any(notif_message in text for text in notif_texts)