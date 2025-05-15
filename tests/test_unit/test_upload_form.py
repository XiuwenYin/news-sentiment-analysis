from app.forms import UploadForm
from werkzeug.datastructures import MultiDict, CombinedMultiDict
from io import BytesIO

# 2.2.1: 单元测试 - UploadForm 验证逻辑
def test_upload_form_valid(app):
    with app.app_context():
        form = UploadForm(
            formdata=CombinedMultiDict([
                MultiDict({
                    "post_title": "Sample News",
                    "news_content": "This is the news content."
                })
            ]),
            meta={"csrf": False}
        )
        assert form.validate() is True


def test_upload_form_missing_title(app):
    with app.app_context():
        form = UploadForm(
            formdata=CombinedMultiDict([
                MultiDict({
                    "news_content": "Some content only."
                })
            ]),
            meta={"csrf": False}
        )
        assert form.validate() is False
        assert "This field is required." in form.post_title.errors


def test_upload_form_missing_content(app):
    with app.app_context():
        form = UploadForm(
            formdata=CombinedMultiDict([
                MultiDict({
                    "post_title": "Only title provided"
                })
            ]),
            meta={"csrf": False}
        )
        assert form.validate() is False
        assert "This field is required." in form.news_content.errors
