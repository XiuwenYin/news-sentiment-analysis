# tests/test_unit/test_user_insight_helper.py
from datetime import datetime
import sqlalchemy as sa
from app import db
from app.models import User, Post
from sqlalchemy import func

# 4.2.1: Unit testing - Insight data aggregation/filtering helper functions (mock DB)
def test_category_distribution_by_gender(app):
    with app.app_context():
        db.create_all()
        # Add two users of different genders
        user1 = User(username="alice", email="alice@example.com", gender="Female")
        user1.set_password("pass")
        user2 = User(username="bob", email="bob@example.com", gender="Male")
        user2.set_password("pass")
        db.session.add_all([user1, user2])
        db.session.commit()

        # Add posts belonging to different categories
        posts = [
            Post(title="p1", body="b1", category="World", sentiment="Positive", author=user1, timestamp=datetime.utcnow()),
            Post(title="p2", body="b2", category="Tech", sentiment="Positive", author=user1, timestamp=datetime.utcnow()),
            Post(title="p3", body="b3", category="World", sentiment="Negative", author=user2, timestamp=datetime.utcnow())
        ]
        db.session.add_all(posts)
        db.session.commit()

        #Query the category distribution of Female
        result = db.session.execute(
            sa.select(Post.category, func.count(Post.id))
            .join(User)
            .where(User.gender == "Female")
            .group_by(Post.category)
        ).all()

        category_distribution = dict(result)
        assert category_distribution == {"World": 1, "Tech": 1}


def test_category_distribution_by_age_group(app):
    with app.app_context():
        db.create_all
        # Add two users with different ages
        user1 = User(username="young", email="young@example.com", age=21)
        user1.set_password("pass")
        user2 = User(username="old", email="old@example.com", age=65)
        user2.set_password("pass")
        db.session.add_all([user1, user2])
        db.session.commit()

        # Add posts
        posts = [
            Post(title="p1", body="b1", category="Sports", sentiment="Positive", author=user1, timestamp=datetime.utcnow()),
            Post(title="p2", body="b2", category="Politics", sentiment="Neutral", author=user2, timestamp=datetime.utcnow())
        ]
        db.session.add_all(posts)
        db.session.commit()

        # Query the category distribution of the age group 18–30
        result = db.session.execute(
            sa.select(Post.category, func.count(Post.id))
            .join(User)
            .where(User.age.between(18, 30))
            .group_by(Post.category)
        ).all()

        category_distribution = dict(result)
        assert category_distribution == {"Sports": 1}
