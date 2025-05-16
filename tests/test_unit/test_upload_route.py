from app.models import User
from app import db

def test_upload_get_returns_200(test_client, app):
    with app.app_context():
        user = User(username="testuser", email="test@example.com")
        user.set_password("testpass")
        db.session.add(user)
        db.session.commit()

    # login
    test_client.post("/auth/login", data={
        "username": "testuser",
        "password": "testpass"
    }, follow_redirects=True)

    response = test_client.get("/upload/upload", follow_redirects=True)

    assert response.status_code == 200
    assert b"Upload" in response.data
