from app.models import User, db
from app.forms import FilterForm
from flask import url_for
from datetime import datetime
import pytest

def test_user_profile_updates_missing_info(test_client, app):
    with app.app_context():
        user = User(username="testuser", email="test@example.com", age=None, gender=None)
        user.set_password("password")
        db.session.add(user)
        db.session.commit()
        user_id = user.id  # save id

    test_client.post("/auth/login", data={
        "username": "testuser",
        "password": "password"
    }, follow_redirects=True)

    response = test_client.post("/user/user/testuser", data={
        "age": "30",
        "gender": "Female"
    }, follow_redirects=True)

    assert response.status_code == 200

    with app.app_context():
        updated_user = db.session.get(User, user_id)
        assert updated_user.age == 30
        assert updated_user.gender == "Female"


def test_user_profile_does_not_overwrite_existing_info(test_client, app):
    with app.app_context():
        user = User(username="existinguser", email="exist@example.com", age=28, gender="Male")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    test_client.post("/auth/login", data={
        "username": "existinguser",
        "password": "password"
    }, follow_redirects=True)

    response = test_client.post("/user/user/existinguser", data={
        "age": "99",
        "gender": "Other"
    }, follow_redirects=True)

    assert response.status_code == 200

    with app.app_context():
        user_check = db.session.get(User, user_id)
        assert user_check.age == 28
        assert user_check.gender == "Male"
