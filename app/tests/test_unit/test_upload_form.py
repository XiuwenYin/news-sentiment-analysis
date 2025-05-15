import unittest
from app import app
from app.forms import UploadForm
from werkzeug.datastructures import MultiDict

app.config.from_object('config.TestingConfig')

# 2.2.1 Unit Test - UploadForm Validation Logic
# Use test configuration: turn off CSRF verification and use in-memory database
# ./venv/bin/python -m unittest discover -s app/tests/test_unit -p "test_upload_form.py"
class TestUploadForm(unittest.TestCase):

    # Run before each test: create app context and request context
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        self.client = app.test_client()
        self.request_context = app.test_request_context()
        self.request_context.push()

    # Run after each test: destroy the context to prevent memory leaks
    def tearDown(self):
        self.request_context.pop()
        self.app_context.pop()

    # Test form: Both the title and content are legal, the verification should pass
    def test_valid_form(self):
        form = UploadForm(formdata=MultiDict({
            'post_title': 'Valid Title',
            'news_content': 'This is valid news content.'
        }))
        self.assertTrue(form.validate())

    # Test form: If the title is empty, the validation should fail and an error message should be returned
    def test_missing_title(self):
        form = UploadForm(formdata=MultiDict({
            'post_title': '',
            'news_content': 'Valid content'
        }))
        self.assertFalse(form.validate())
        self.assertIn('This field is required.', form.post_title.errors)

    # Test form: If the content is empty, the verification should fail and an error message should be returned
    def test_missing_content(self):
        form = UploadForm(formdata=MultiDict({
            'post_title': 'Valid Title',
            'news_content': ''
        }))
        self.assertFalse(form.validate())
        self.assertIn('This field is required.', form.news_content.errors)

    # Test form: The title is too long (over 101 characters), currently no length limit set, the verification be successful
    def test_title_too_long(self):
        form = UploadForm(formdata=MultiDict({
            'post_title': 'A' * 101,
            'news_content': 'Valid content'
        }))
        self.assertTrue(form.validate())  # 因为你目前没加长度限制，所以应为 True

    # Test form: The content is too long (501 characters), currently no length limit set, the verification should be successful
    def test_content_too_long(self):
        form = UploadForm(formdata=MultiDict({
            'post_title': 'Valid Title',
            'news_content': 'A' * 501
        }))
        self.assertTrue(form.validate()) 

# Unit test entry
if __name__=='__main__':
    unittest.main()
