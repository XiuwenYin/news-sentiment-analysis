from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash

# Association table to track which posts are shared with which users
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
    
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    profile_completed: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False, nullable=False)

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
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)
    
    # Many-to-many relationship: post ←→ users it is shared with
    shared_with: so.WriteOnlyMapped[list['User']] = so.relationship(
        'User',
        secondary='post_shares',
        back_populates='shared_posts'
    )

    sentiment: so.Mapped[str] = so.mapped_column(sa.String(64), nullable=True)
    #label: so.Mapped[str] = so.mapped_column(sa.String(64), nullable=True)
    author: so.Mapped[User] = so.relationship(back_populates='posts')
    # News category and sentiment score
    category: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64), nullable=True)
    emotions: so.Mapped[Optional[dict]] = so.mapped_column(sa.JSON, nullable=True) 

    def __repr__(self):
        return '<Post {}>'.format(self.body)
    
    
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))



class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    message = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref='notifications')

    def __repr__(self):
        return f'<Notification {self.message}>'
