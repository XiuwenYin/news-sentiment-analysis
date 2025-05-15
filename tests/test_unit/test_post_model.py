import unittest
from datetime import datetime
from app import app, db
from app.models import Post

class TestPostModel(unittest.TestCase):
    # Execute before each test: Create a test database environment
    def setUp(self):
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    # Execute after each test: clean up the database environment
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # 2.1.1 Test whether the creation of a new post is successful and whether the fields are saved correctly
    def test_create_post(self):
        post = Post(
            title="Test Title",
            body="This is a test post body",
            sentiment="Positive",
            user_id=1
        )
        db.session.add(post)
        db.session.commit()

        queried = Post.query.first()
        self.assertEqual(queried.title, "Test Title")
        self.assertEqual(queried.body, "This is a test post body")
        self.assertEqual(queried.sentiment, "Positive")
        self.assertEqual(queried.user_id, 1)
        self.assertIsInstance(queried.timestamp, datetime)

    # 2.1.3 Test the __repr__ string representation of the Post model
    def test_repr_method(self):
        post = Post(title="X", body="Y")
        self.assertIn("Post", repr(post))  # Basic check

    # 2.1.2 Test whether the sentiment field can be assigned and read correctly
    def test_sentiment_field(self):
        post = Post(
            title="Feeling test",
            body="Mood swings",
            sentiment="Neutral",
            user_id=2
        )
        db.session.add(post)
        db.session.commit()

        queried = Post.query.first()
        self.assertEqual(queried.sentiment, "Neutral")

# Run the test main entry
if __name__=='__main__':
    unittest.main()
