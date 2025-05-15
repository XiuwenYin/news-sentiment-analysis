# tests/test_unit/test_user_model.py
import pytest
from app.models import User
from app import db
from sqlalchemy.exc import IntegrityError # 导入特定的异常类型

@pytest.fixture(scope='function')
def persisted_user_id(app, init_database): # 修改：返回 ID 而不是对象
    """Creates a user, saves it to the database, and returns its ID."""
    with app.app_context():
        user = User(username='test_persisted', email='persisted@example.com')
        user.set_password('a_strong_password')
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        return user_id # 返回 ID

# --- 测试 User 模型 ---

def test_new_user_creation(new_user): # 使用 conftest.py 中的 new_user
    """测试计划 1.1.1: 单元测试 - 新用户创建"""
    assert new_user.username == 'testuser'
    assert new_user.email == 'test@example.com'
    assert new_user.password_hash is None
    # 断言 profile_completed，期望 new_user fixture 能正确处理默认值
    # 如果 conftest.py 中的 new_user fixture 修改后仍有问题，可以暂时注释此行
    assert new_user.profile_completed is False, \
        f"Expected profile_completed to be False, but got {new_user.profile_completed}"

def test_set_password(new_user):
    """测试计划 1.1.2 (部分): 密码设置"""
    new_user.set_password('cat')
    assert new_user.password_hash is not None
    assert new_user.password_hash != 'cat'

def test_check_password(new_user):
    """测试计划 1.1.2 (部分): 密码验证"""
    new_user.set_password('dog')
    assert new_user.check_password('dog') is True
    assert new_user.check_password('cat') is False

def test_password_hashes_are_random(new_user): # new_user 在这里只是为了获取 User 类
    """测试计划 1.1.2 (部分): 确保同一密码生成不同的哈希 (加盐)"""
    # 创建两个独立的用户实例进行比较
    u1 = User(username='user1_rand', email='user1_rand@example.com')
    u1.set_password('commonpassword')

    u2 = User(username='user2_rand', email='user2_rand@example.com')
    u2.set_password('commonpassword')

    assert u1.password_hash is not None
    assert u2.password_hash is not None
    assert u1.password_hash != u2.password_hash

def test_user_representation(new_user):
    """测试计划 1.1.3: 用户模型字符串表示"""
    assert repr(new_user) == '<User testuser>'

def test_user_creation_in_db(app, init_database):
    """测试计划 1.1.1 (部分): 测试用户创建并能从数据库中检索"""
    with app.app_context():
        u = User(username='dbuser', email='db@example.com', age=30, gender='male')
        u.set_password('securepass123')
        u.profile_completed = True # 显式设置为 True 进行测试

        db.session.add(u)
        db.session.commit()

        # 使用 user_id 进行查询，确保获取的是最新的持久化状态
        retrieved_user = db.session.get(User, u.id)

        assert retrieved_user is not None
        assert retrieved_user.username == 'dbuser'
        assert retrieved_user.email == 'db@example.com'
        assert retrieved_user.check_password('securepass123')
        assert retrieved_user.age == 30
        assert retrieved_user.gender == 'male'
        assert retrieved_user.profile_completed is True

def test_username_uniqueness(app, init_database, persisted_user_id): # 修改：使用 persisted_user_id
    """测试计划 (隐含): 确保用户名字段的唯一性约束"""
    with app.app_context():
        existing_user = db.session.get(User, persisted_user_id)
        assert existing_user is not None, "Persisted user not found in DB by ID"

        duplicate_user = User(username=existing_user.username, email='another@example.com')
        db.session.add(duplicate_user)
        with pytest.raises(IntegrityError): # 使用具体的 IntegrityError
            db.session.commit()
        db.session.rollback() # 回滚失败的事务

def test_email_uniqueness(app, init_database, persisted_user_id): # 修改：使用 persisted_user_id
    """测试计划 (隐含): 确保邮箱字段的唯一性约束"""
    with app.app_context():
        existing_user = db.session.get(User, persisted_user_id)
        assert existing_user is not None, "Persisted user not found in DB by ID"

        duplicate_email_user = User(username='anotheruser', email=existing_user.email)
        db.session.add(duplicate_email_user)
        with pytest.raises(IntegrityError): # 使用具体的 IntegrityError
            db.session.commit()
        db.session.rollback()

