import unittest
from app import create_app, db
from app.models import User, Notification

# ✅ 修正配置，避免路径报错
class FixedTestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # ✅ 使用内存数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'testkey'

class TestNotificationRoutes(unittest.TestCase):

    def setUp(self):
        self.app = create_app(FixedTestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # ✅ 创建用户
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password("testpass")
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_notification(self):
        notif = Notification(message='Test message', user_id=self.user.id)
        db.session.add(notif)
        db.session.commit()

        found = Notification.query.filter_by(user_id=self.user.id).first()
        self.assertIsNotNone(found)
        self.assertEqual(found.message, 'Test message')

    def test_get_notifications_route(self):
        notif = Notification(message='Hello!', user_id=self.user.id)
        db.session.add(notif)
        db.session.commit()

        with self.app.test_client() as client:
            # ✅ 模拟登录用户
            with client.session_transaction() as sess:
                sess['_user_id'] = str(self.user.id)

            res = client.get('/notifications/notifications')
            self.assertEqual(res.status_code, 200)
            self.assertIn(b'Hello!', res.data)

    def test_mark_notification_read_route(self):
        notif = Notification(message='Unread msg', user_id=self.user.id, is_read=False)
        db.session.add(notif)
        db.session.commit()

        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess['_user_id'] = str(self.user.id)

            res = client.post('/notifications/mark_notification_read')
            self.assertEqual(res.status_code, 200)

            updated = db.session.get(Notification, notif.id)
            self.assertTrue(updated.is_read)

if __name__ == '__main__':
    unittest.main()
