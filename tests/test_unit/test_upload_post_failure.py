from app.models import Post
from app import db

# 2.2.4: 单元测试 - upload 路由 (POST失败 - 缺失标题/内容)
def test_upload_missing_title(test_client, app, new_user):
    with app.app_context():
        db.session.add(new_user)
        new_user.set_password("password")
        db.session.commit()

        test_client.post("/auth/login", data={
            "username": new_user.username,
            "password": "password"
        }, follow_redirects=True)

        # 提交缺失标题
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

        # 提交缺失内容
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

        # 提交完全为空表单
        response = test_client.post("/upload/upload", data={
            "post_title": "",
            "news_content": ""
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b"This field is required" in response.data
        assert Post.query.count() == 0
