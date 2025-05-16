import unittest
from app import create_app, db
from app.models import User, Notification

# ✅ 直接在代码里定义一个测试配置，避免路径问题
class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # ✅ 使用内存数据库，避免 OperationalError
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test'

class TestNotificationModel(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # 创建一个测试用户
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('password123')
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_notification(self):
        notif = Notification(message='Test Msg', user_id=self.user.id)
        db.session.add(notif)
        db.session.commit()

        self.assertIsNotNone(notif.id)
        self.assertEqual(notif.message, 'Test Msg')
        self.assertFalse(notif.is_read)

    def test_mark_notification_read_unread(self):
        notif = Notification(message='Another Msg', user_id=self.user.id)
        db.session.add(notif)
        db.session.commit()

        self.assertFalse(notif.is_read)

        notif.is_read = True
        db.session.commit()
        self.assertTrue(notif.is_read)

if __name__ == '__main__':
    unittest.main()
