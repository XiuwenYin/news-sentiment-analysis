from app.models import Post, User
from app import db

def test_upload_missing_title(test_client, app, new_user):
    with app.app_context():
        user = User(username="user1", email="user1@example.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        test_client.post("/auth/login", data={
            "username": "user1",
            "password": "password"
        }, follow_redirects=True)

        response = test_client.post("/upload/upload", data={
            "post_title": "",
            "news_content": "Some content here"
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b"This field is required" in response.data
        assert Post.query.count() == 0


def test_upload_missing_content(test_client, app):
    with app.app_context():
        user = User(username="user2", email="user2@example.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        test_client.post("/auth/login", data={
            "username": "user2",
            "password": "password"
        }, follow_redirects=True)

        response = test_client.post("/upload/upload", data={
            "post_title": "Valid Title",
            "news_content": ""
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b"This field is required" in response.data
        assert Post.query.count() == 0


def test_upload_missing_all(test_client, app):
    with app.app_context():
        user = User(username="user3", email="user3@example.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        test_client.post("/auth/login", data={
            "username": "user3",
            "password": "password"
        }, follow_redirects=True)

        response = test_client.post("/upload/upload", data={
            "post_title": "",
            "news_content": ""
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b"This field is required" in response.data
        assert Post.query.count() == 0
