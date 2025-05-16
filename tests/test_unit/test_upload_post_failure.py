from app.models import Post
from app import db

# 2.2.4: Unit Testing - upload route (POST fails - missing headers/content)
def test_upload_missing_title(test_client, app, new_user):
    with app.app_context():
        db.session.add(new_user)
        new_user.set_password("password")
        db.session.commit()

        test_client.post("/auth/login", data={
            "username": new_user.username,
            "password": "password"
        }, follow_redirects=True)

        # Commit missing headers
        response = test_client.post("/upload/upload", data={
            "post_title": "",
            "news_content": "Some content here"
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b"This field is required" in response.data
        assert Post.query.count() == 0


def test_upload_missing_content(test_client, app, new_user):
    with app.app_context():
        db.session.add(new_user)
        new_user.set_password("password")
        db.session.commit()

        test_client.post("/auth/login", data={
            "username": new_user.username,
            "password": "password"
        }, follow_redirects=True)

        # Submit missing content
        response = test_client.post("/upload/upload", data={
            "post_title": "Valid Title",
            "news_content": ""
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b"This field is required" in response.data
        assert Post.query.count() == 0


def test_upload_missing_all(test_client, app, new_user):
    with app.app_context():
        db.session.add(new_user)
        new_user.set_password("password")
        db.session.commit()

        test_client.post("/auth/login", data={
            "username": new_user.username,
            "password": "password"
        }, follow_redirects=True)

        # Submit a completely empty form
        response = test_client.post("/upload/upload", data={
            "post_title": "",
            "news_content": ""
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b"This field is required" in response.data
        assert Post.query.count() == 0
