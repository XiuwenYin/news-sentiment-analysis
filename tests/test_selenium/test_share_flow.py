import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests.test_selenium.test_auth_flows import robust_click

def test_share_analysis_flow(browser, live_server, user_with_post, app):
    driver = browser
    base_url = live_server.url()
    username = user_with_post["username"]
    password = user_with_post["password"]

    # Log in
    driver.get(base_url + "/auth/login")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    robust_click(driver, (By.CSS_SELECTOR, "button[type='submit'],input[type='submit']"))
    WebDriverWait(driver, 10).until(EC.url_contains("/index") or EC.url_matches(r"/$"))

    # Go to Share page
    driver.get(base_url + "/share/share")

    # Click "Share a New Analysis" button robustly
    robust_click(driver, (By.XPATH, "//button[contains(text(), 'Share a New Analysis')]"))

    # Wait for modal to appear and select an analysis
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "sharePostModal"))
    )
    # Step 1: Select an analysis
    post_select = driver.find_element(By.NAME, "post_id")
    options = post_select.find_elements(By.TAG_NAME, "option")
    for option in options:
        if option.get_attribute("value"):
            option.click()
            break

    # Go to Step 2
    next_btn = driver.find_element(By.ID, "nextStep")
    next_btn.click()

    # Step 2: Select a user
    user_select = driver.find_element(By.NAME, "user_id")
    user_options = user_select.find_elements(By.TAG_NAME, "option")
    for option in user_options:
        if option.get_attribute("value"):
            option.click()
            break

    # Submit the share
    submit_btn = driver.find_element(By.ID, "submitShare")
    submit_btn.click()

    # Check for a success message or UI update (adjust selector/message as needed)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "alert"))
    )
    alert = driver.find_element(By.CLASS_NAME, "alert")
    assert "shared" in alert.text.lower() or "success" in alert.text.lower()
