import unittest
from unittest.mock import patch
from app import app, db
from app.models import User, Post

app.config.from_object('config.TestingConfig')


# 2.2.3 Unit Test - Test the POST submission logic of the /upload route (success path)
# This test class is used to verify whether the POST request of the upload page can be submitted normally and whether the page contains the upload form fields.
# ./venv/bin/python -m unittest discover -s app/tests/test_unit -p "test_upload_post_success.py"
class TestUploadPostSuccess(unittest.TestCase):

    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        self.client = app.test_client()
        db.create_all()

        user = User(username="testuser", email="test@example.com")
        user.set_password("testpass")
        db.session.add(user)
        db.session.commit()

        self.client.post("/login", data={
            "username": "testuser",
            "password": "testpass"
        }, follow_redirects=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @patch("app.routes.sentiment_classifier")
    @patch("app.routes.emotion_classifier")
    @patch("app.routes.news_category_classifier")
    def test_upload_post_success(self, mock_category, mock_emotion, mock_sentiment):


        # Set mock return value
        mock_sentiment.return_value = [{"label": "LABEL_2", "score": 0.98}]
        mock_emotion.return_value = [[{"label": "joy", "score": 0.95}]]
        mock_category.return_value = [[{"label": "World"}]]

        # Submit the upload form
        response = self.client.post("/upload", data={
            "post_title": "Test News",
            "news_content": "This is some test news content to analyze."
        }, follow_redirects=True)

        html = response.get_data(as_text=True)

        # Verify the response status code
        self.assertEqual(response.status_code, 200)

        # Verify that the page contains analysis results
        self.assertIn("This is some test news content to analyze.", html)
        self.assertIn("Positive", html)  # sentiment_label_map["LABEL_2"]
        self.assertIn("World", html)
        self.assertIn("Joy", html)

        # Verify that the post has been added to the database
        post = Post.query.filter_by(title="Test News").first()
        self.assertIsNotNone(post)
        self.assertEqual(post.sentiment, "Positive")
        self.assertEqual(post.category, "World")


if __name__=="__main__":
    unittest.main()
