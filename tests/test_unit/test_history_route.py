# tests/test_unit/test_history_route.py

# 3.2.1: Unit Testing - Testing the History Routing
from app.models import User, Post
from app import db
from datetime import datetime

def test_history_route_displays_user_posts(test_client, app):
    with app.app_context():
        user = User(username="testuser", email="test@example.com")
        user.set_password("testpass")
        db.session.add(user)
        db.session.commit()

    test_client.post("/auth/login", data={
        "username": "testuser",
        "password": "testpass"
    }, follow_redirects=True)

    with app.app_context():
        user_in_db = User.query.filter_by(username="testuser").first()
        post1 = Post(title="Post One", body="Test Content 1", author=user_in_db, timestamp=datetime.now())
        post2 = Post(title="Post Two", body="Test Content 2", author=user_in_db, timestamp=datetime.now())
        db.session.add_all([post1, post2])
        db.session.commit()

    response = test_client.get("/history/history", follow_redirects=True)

    assert response.status_code == 200
    assert b"Post One" in response.data
    assert b"Post Two" in response.data
