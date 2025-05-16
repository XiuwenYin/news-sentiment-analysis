# tests/test_unit/test_user_insight_route.py

from datetime import datetime, timedelta
from app.models import User, Post, db

def test_user_insight_route_shows_chart_data(app, test_client):
    with app.app_context():
        # create a test user
        user = User(username="insightuser", email="insight@example.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        # login
        test_client.post("/auth/login", data={
            "username": "insightuser",
            "password": "password"
        }, follow_redirects=True)

        # Add test posts from the last 7 days (with different sentiments and categories)
        now = datetime.utcnow()
        posts = [
            Post(title="News1", body="Body1", sentiment="Positive", category="World", author=user, timestamp=now - timedelta(days=1)),
            Post(title="News2", body="Body2", sentiment="Negative", category="Tech", author=user, timestamp=now - timedelta(days=2)),
            Post(title="News3", body="Body3", sentiment="Neutral", category="World", author=user, timestamp=now - timedelta(days=3)),
        ]
        db.session.add_all(posts)
        db.session.commit()

        # Initiat a GET request
        response = test_client.get(f"/user/user/{user.username}", follow_redirects=True)

        assert response.status_code == 200
        html = response.data.decode("utf-8")

        # Check if relevant data for the chart is included (sentiment, category, etc.)
        assert "Positive" in html
        assert "Negative" in html
        assert "Neutral" in html
        assert "World" in html
        assert "Tech" in html

