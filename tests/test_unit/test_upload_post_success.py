from unittest.mock import patch
from werkzeug.datastructures import MultiDict
from app.models import Post

def test_upload_post_success(test_client, app, new_user):
    with app.app_context():
        from app import db
        new_user.set_password("testpass")
        db.session.add(new_user)
        db.session.commit()

        # 登录
        login_data = {
            "username": new_user.username,
            "password": "testpass"
        }
        test_client.post("/auth/login", data=login_data, follow_redirects=True)

        # patch 的路径指向 upload_routes
        with patch("app.routes.upload_routes.sentiment_classifier") as mock_sentiment, \
             patch("app.routes.upload_routes.news_category_classifier") as mock_category, \
             patch("app.routes.upload_routes.news_summarizer") as mock_summarizer, \
             patch("app.routes.upload_routes.emotion_classifier") as mock_emotion:

            mock_sentiment.return_value = [{"label": "LABEL_2", "score": 0.95}]
            mock_category.return_value = [[{"label": "World", "score": 0.99}]]
            mock_summarizer.return_value = [{"summary_text": "This is a summary."}]
            mock_emotion.return_value = [[
                {"label": "joy", "score": 0.9},
                {"label": "sadness", "score": 0.1}
            ]]

            data = {
                "post_title": "Test Title",
                "news_content": "This is some test news content."
            }
            response = test_client.post("/upload/upload", data=data, follow_redirects=True)

            assert response.status_code == 200
            assert b"This is a summary." in response.data
