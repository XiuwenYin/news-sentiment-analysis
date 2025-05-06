from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from flask_login import UserMixin


from werkzeug.security import generate_password_hash, check_password_hash

post_shares = sa.Table(
    'post_shares',
    db.metadata,
    sa.Column('post_id', sa.Integer, sa.ForeignKey('post.id'), primary_key=True),
    sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, 
                                                unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, 
                                             unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    posts: so.WriteOnlyMapped['Post'] = so.relationship(
        back_populates='author')
    
    # Add a relationship to track posts shared with the user
    shared_posts: so.WriteOnlyMapped[list['Post']] = so.relationship(
        'Post',
        secondary='post_shares',
        back_populates='shared_with'
    )

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    

class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(100))
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    sentiment: so.Mapped[Optional[str]] = so.mapped_column(sa.String(20), nullable=True)
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)
    
    shared_with: so.WriteOnlyMapped[list['User']] = so.relationship(
        'User',
        secondary='post_shares',
        back_populates='shared_posts'
    )

    # 情感分析字数统计：新增字段
    sentiment: so.Mapped[str] = so.mapped_column(sa.String(64), nullable=True)

    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self):
        return '<Post {}>'.format(self.body)
    
    
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))