# tests/test_selenium/test_auth_flows.py
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import time

def generate_unique_string(prefix="test"):
    return f"{prefix}_{int(time.time() * 1000)}"

def robust_click(driver, element_or_locator, timeout=20):
    if isinstance(element_or_locator, tuple):
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(element_or_locator)
        )
    else:
        element = element_or_locator
        WebDriverWait(driver, timeout).until(lambda d: element.is_displayed() and element.is_enabled())

    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", element)
        time.sleep(0.5) 
        element.click()
    except ElementClickInterceptedException as e_click_intercept:
        print(f"DEBUG_CLICK: Regular click intercepted for {element_or_locator}: {e_click_intercept}. Trying JavaScript click.")
        driver.save_screenshot(f"debug_click_intercepted_{generate_unique_string('err')}.png")
        try:
            driver.execute_script("arguments[0].click();", element)
        except Exception as e_js_click:
            print(f"DEBUG_CLICK: JavaScript click ALSO FAILED for {element_or_locator}: {e_js_click}")
            driver.save_screenshot(f"debug_js_click_failed_{generate_unique_string('err')}.png")
            raise 
    except Exception as e_other_click:
        print(f"DEBUG_CLICK: Other error during click for {element_or_locator}: {e_other_click}")
        driver.save_screenshot(f"debug_other_click_error_{generate_unique_string('err')}.png")
        raise

def test_successful_registration(browser, live_server):
    driver = browser
    base_url = live_server.url()
    driver.get(base_url + "/auth/register")

    unique_username = generate_unique_string("user")
    unique_email = f"{unique_username}@example.com"
    password = "SecurePassword123!"

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(unique_username)
    driver.find_element(By.NAME, "email").send_keys(unique_email)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "password2").send_keys(password)

    submit_button_locator = (By.XPATH, "//input[@type='submit' and @value='Register']")
    robust_click(driver, submit_button_locator)

    WebDriverWait(driver, 10).until(EC.url_contains("/auth/login"))
    assert "/auth/login" in driver.current_url

    try:
        flash_message = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//*[contains(@class, 'flash') or contains(@class, 'alert')]"))
        )
        assert "Congratulations, you are now a registered user!" in flash_message.text
    except TimeoutException:
        driver.save_screenshot("debug_registration_flash_timeout.png")
        pytest.fail("Registration success message not found due to timeout.")
    except AssertionError as e: # Catch AssertionError specifically for text mismatch
        driver.save_screenshot("debug_registration_flash_text_mismatch.png")
        pytest.fail(f"Registration success flash message text mismatch: {e}")
    except Exception as e: # Catch any other unexpected exceptions
        driver.save_screenshot("debug_registration_flash_general_error.png")
        pytest.fail(f"Error during registration flash message validation: {e}")

@pytest.fixture(scope='function')
def registered_user_for_login(app, init_database):
    from app.models import User
    from app import db as app_db
    with app.app_context():
        username = generate_unique_string("loginuser_fix")
        email = f"{username}@example.com"
        password_plain = "LoginPassword456!"
        print(f"FIXTURE: Attempting to create user: {username}, email: {email}, pass: {password_plain}")
        user = User(username=username, email=email)
        user.set_password(password_plain)
        app_db.session.add(user)
        try:
            app_db.session.commit()
            print(f"FIXTURE: User {username} created and committed. ID: {user.id}, Password Hash: {user.password_hash[:20] if user.password_hash else 'None'}...")
        except Exception as e:
            print(f"FIXTURE: Error committing user {username}: {e}")
            app_db.session.rollback(); raise
        retrieved_user = app_db.session.get(User, user.id)
        if not (retrieved_user and retrieved_user.check_password(password_plain)):
            pytest.fail("User creation or password verification failed in fixture.")
        print(f"FIXTURE: Password for {retrieved_user.username} verified successfully in fixture.")
        return {"username": username, "password": password_plain, "email": email}

def test_successful_login(browser, live_server, registered_user_for_login, app):
    driver = browser
    base_url = live_server.url()
    user_credentials = registered_user_for_login
    driver.get(base_url + "/auth/login")

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(user_credentials["username"])
    driver.find_element(By.NAME, "password").send_keys(user_credentials["password"])

    submit_button_locator = (By.XPATH, "//input[@type='submit' and @value='Sign In']")
    robust_click(driver, submit_button_locator)

    expected_redirect_url_part = "/index"
    try:
        WebDriverWait(driver, 15).until(EC.url_contains(expected_redirect_url_part))
    except TimeoutException as e_url:
        print(f"TIMEOUT WAITING FOR URL to contain '{expected_redirect_url_part}'. Current URL: {driver.current_url}")
        driver.save_screenshot("debug_login_url_timeout.png"); raise e_url
    assert expected_redirect_url_part in driver.current_url

    try:
        logout_link = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.LINK_TEXT, "Logout")))
        assert logout_link.is_displayed()
    except TimeoutException as e_logout:
        print(f"TIMEOUT WAITING FOR LOGOUT LINK. Current URL: {driver.current_url}")
        driver.save_screenshot("debug_login_logout_link_timeout.png"); raise e_logout
    except AssertionError as e:
        driver.save_screenshot("debug_login_logout_link_assertion_fail.png")
        pytest.fail(f"Logout link assertion failed: {e}")
    except Exception as e:
        driver.save_screenshot("debug_login_logout_link_general_error.png")
        pytest.fail(f"Error during logout link validation: {e}")


def test_login_failure_invalid_credentials(browser, live_server):
    driver = browser
    base_url = live_server.url()
    driver.get(base_url + "/auth/login")

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("nonexistentuser")
    driver.find_element(By.NAME, "password").send_keys("wrongpassword")
    
    submit_button_locator = (By.XPATH, "//input[@type='submit' and @value='Sign In']")
    robust_click(driver, submit_button_locator)

    WebDriverWait(driver, 10).until(EC.url_contains("/auth/login"))
    assert "/auth/login" in driver.current_url

    try:
        error_message = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//*[contains(@class, 'flash') or contains(@class, 'alert')]"))
        )
        assert "Invalid username or password" in error_message.text
    except TimeoutException:
        driver.save_screenshot("debug_login_fail_flash_timeout.png")
        pytest.fail("Login error flash message not found due to timeout.")
    except AssertionError as e:
        driver.save_screenshot("debug_login_fail_flash_text_mismatch.png")
        pytest.fail(f"Login error flash message text mismatch: {e}")
    except Exception as e:
        driver.save_screenshot("debug_login_fail_flash_general_error.png")
        pytest.fail(f"Error during login failure flash message validation: {e}")