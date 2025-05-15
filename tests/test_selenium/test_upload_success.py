# import time
# import pytest
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys

# def test_text_upload_success(test_user_login):
#     browser = test_user_login

#     browser.fill("post_title", "Test Title")
#     browser.fill("post_content", "This is test content for upload.")

#     browser.find_by_value("Upload").first.click()

#     print(browser.html)
#     assert browser.is_text_present("Upload successful", wait_time=5)
#     print(browser.html)

