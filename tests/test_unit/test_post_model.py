from app.models import Post
from datetime import datetime
import pytest

# 2.1 New post creation, sentiment analysis result access, and other Post model-specific methods
def test_create_post(app, init_database, new_user):
    # 2.1.1: 新帖子创建
    with app.app_context():
        post = Post(
            title="Test Title",
            body="This is a test body.",
            author=new_user  # 需要是已存在数据库中的 user
        )
        from app import db
        db.session.add(new_user)
        db.session.add(post)
        db.session.commit()

        saved_post = Post.query.first()
        assert saved_post.title == "Test Title"
        assert saved_post.body == "This is a test body."
        assert saved_post.author.username == "testuser"
        assert isinstance(saved_post.timestamp, datetime)


def test_post_sentiment_fields(app, init_database, new_user):
    # 2.1.2: 情感分析结果存取
    with app.app_context():
        post = Post(
            title="Emotion Post",
            body="Body for emotion post",
            author=new_user,
            sentiment="Positive",
            category="World",
            emotions={"joy": 0.8, "sadness": 0.1}
        )
        from app import db
        db.session.add(new_user)
        db.session.add(post)
        db.session.commit()

        loaded_post = Post.query.filter_by(title="Emotion Post").first()
        assert loaded_post.sentiment == "Positive"
        assert loaded_post.category == "World"
        assert isinstance(loaded_post.emotions, dict)
        assert "joy" in loaded_post.emotions
        assert loaded_post.emotions["joy"] == 0.8


def test_post_repr_method(app, init_database, new_user):
    # 2.1.3: Post模型特有方法 (__repr__)
    with app.app_context():
        post = Post(title="Repr Test", body="...", author=new_user)
        from app import db
        db.session.add(new_user)
        db.session.add(post)
        db.session.commit()

        assert repr(post).startswith("<Post")
