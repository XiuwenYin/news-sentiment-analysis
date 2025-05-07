from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import sqlalchemy as sa
from app import db
from app.models import User
from wtforms import TextAreaField

class LoginForm(FlaskForm):
    # Form for user login
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    # Form for new user registration
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    # Validate if username already exists
    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')

    # Validate if email already exists
    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')
        
class UploadForm(FlaskForm):
    # Form for uploading news content for sentiment analysis
    news_content = TextAreaField('News Content', validators=[DataRequired()])
    submit = SubmitField('Upload and Analyze')

class SharePostForm(FlaskForm):
    # Form for sharing a post with another user
    post_id = StringField('Post ID', validators=[DataRequired()])
    user_id = StringField('User ID', validators=[DataRequired()])
    submit = SubmitField('Share')