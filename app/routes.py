from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa

from app.models import User, Post, db, post_shares
from flask import render_template, flash, redirect, url_for, request

from app import app, db
from app.forms import LoginForm, RegistrationForm, SharePostForm, UploadForm
from urllib.parse import urlsplit
from transformers import pipeline

import re

#日期分组创建字典
from collections import defaultdict

# from flask_wtf import csrf
from app import csrf

# Perform a label among positive, negative, and neutral.
sentiment_classifier = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")
sentiment_label_map = {
    "LABEL_0": "Negative",
    "LABEL_1": "Neutral",
    "LABEL_2": "Positive"
}

# Predict emotion among anger, disgust, fear, joy, neutral, sadnes, surprise.
#
# Output example:
# [[{'label': 'anger', 'score': 0.004419783595949411},
#   {'label': 'disgust', 'score': 0.0016119900392368436},
#   {'label': 'fear', 'score': 0.0004138521908316761},
#   {'label': 'joy', 'score': 0.9771687984466553},
#   {'label': 'neutral', 'score': 0.005764586851000786},
#   {'label': 'sadness', 'score': 0.002092392183840275},
#   {'label': 'surprise', 'score': 0.008528684265911579}]]
# 每个输出要自己从中提取出最高的
emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=True)


@app.route("/")
@app.route("/index")
# @login_required
def index():
    return render_template("homepage.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    # if the form is not submitted or invalid, render the login page
    return render_template("login.html",
        title="Login",
        hero_title="Sign In to Your Account",
        hero_subtitle="Access your dashboard, share results, and more",
        hero_button_text=None,
        hero_button_link=None,
        form=form 
    )


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("login"))
    return render_template("register.html",form=form)


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if not current_user.is_authenticated:
        flash("You need to log in to upload news content.", "warning")
        return redirect(url_for("index"))

    form = UploadForm()
    if form.validate_on_submit():
        post_title = request.form["post_title"]
        news_content = form.news_content.data

        # 文字统计
        char_count = len(news_content)
        sentence_count = len([s for s in re.split(r'[.!?]', news_content) if s.strip()])

         # 情绪分析：先获取结果并排序
        emotion_scores = emotion_classifier(news_content)[0]
        emotion_scores_sorted = sorted(emotion_scores, key=lambda x: x['score'], reverse=True)

        # 情感倾向分析（positive/neutral/negative）
        sentiment_output = sentiment_classifier(news_content)
        sentiment = sentiment_label_map[sentiment_output[0]["label"]]

        # 保存到数据库
        post = Post(title=post_title, body=news_content, author=current_user)
        post.sentiment = sentiment
        db.session.add(post)
        db.session.commit()

        # 渲染页面，包括情绪和情感倾向
        return render_template("visualize.html",
                               content=news_content,
                               result=sentiment,
                               char_count=char_count,
                               sentence_count=sentence_count,
                               emotion_scores=emotion_scores_sorted)

    return render_template("upload.html", form=form)


@app.route("/share")
@login_required
def share():
    # Query the shared posts explicitly
    shared_posts = db.session.scalars(
        sa.select(Post).join(post_shares).where(post_shares.c.user_id == current_user.id)
    ).all()
    user_posts = Post.query.filter_by(user_id=current_user.id).all()
    other_users = User.query.filter(User.id != current_user.id).all()
    form = SharePostForm()

    return render_template(
        "share.html", 
        shared_posts=shared_posts, 
        user_posts=user_posts, 
        other_users=other_users,
        form=form,
        )


@app.route('/share_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def share_post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        usernames = request.form.getlist('usernames')  # List of usernames to share with
        for username in usernames:
            user = User.query.filter_by(username=username).first()
            if user and user not in post.shared_with:
                post.shared_with.append(user)
        db.session.commit()
        flash('Post shared successfully!', 'success')
        return redirect(url_for('share'))

    users = User.query.filter(User.id != current_user.id).all()  # Exclude the current user
    return render_template('share_post.html', post=post, users=users)


@app.route('/share_post_modal', methods=['POST'])
@login_required
def share_post_modal():
    post_id = request.form.get('post_id')
    user_id = request.form.get('user_id')

    post = Post.query.get_or_404(post_id)
    user = User.query.get_or_404(user_id)

    # Check if the post is already shared with the user
    existing_share = db.session.execute(
        sa.select(post_shares).where(
            post_shares.c.post_id == post.id,
            post_shares.c.user_id == user.id
        )
    ).first()

    if not existing_share:
        # Add a new entry to the post_shares table
        db.session.execute(
            post_shares.insert().values(post_id=post.id, user_id=user.id)
        )
        db.session.commit()
        flash(f'Post "{post.title}" shared with {user.username}!', 'success')
    else:
        flash(f'Post "{post.title}" is already shared with {user.username}.', 'info')

    return redirect(url_for('share'))


@app.route("/history")
@login_required
def history():
    posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.timestamp.desc()).all()
    
    grouped_posts = defaultdict(list)
    for post in posts:
        date_str = post.timestamp.strftime('%Y-%m-%d')  # 按天归类
        grouped_posts[date_str].append(post)

    return render_template("history.html", grouped_posts=grouped_posts)

@app.route("/post/<int:post_id>")
@login_required
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    char_count = len(post.body)
    sentence_count = len([s for s in re.split(r'[.!?]', post.body) if s.strip()])
    return render_template("visualize.html", content=post.body, result=post.sentiment,
                           char_count=char_count, sentence_count=sentence_count)


@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    posts = db.session.execute(
        sa.select(Post).where(Post.user_id == user.id).order_by(Post.timestamp.desc())
        ).scalars().all()
    
    # Calculate label counts
    label_counts = {
        'Negative': sum(1 for post in posts if post.sentiment == 'Negative'),
        'Neutral': sum(1 for post in posts if post.sentiment == 'Neutral'),
        'Positive': sum(1 for post in posts if post.sentiment == 'Positive')
    }

    return render_template('user.html', user=user, posts=posts, label_counts=label_counts)


@app.route('/post/<int:post_id>')
@login_required
def post(post_id):
    post = db.first_or_404(sa.select(Post).where(Post.id == post_id))
    return render_template('post.html', post=post)

@app.route('/analysis', methods=['GET', 'POST'])
def analysis():
    label_map = {
        "LABEL_0": "Negative",
        "LABEL_1": "Neutral",
        "LABEL_2": "Positive"
    }

    result = None
    emotion_result = None

    if request.method == 'POST':
        text_input = request.form.get('textInput', '')

        # 情感倾向分析
        output = sentiment_classifier(text_input)
        sentiment = label_map[output[0]["label"]]
        confidence = output[0]["score"]
        result = f"Sentiment: {sentiment} ({confidence:.2%} confidence)"

        # 情绪分析，细化
        emotion_scores = emotion_classifier(text_input)[0]
        top_emotion = max(emotion_scores, key=lambda x: x['score'])
        emotion_result = f"Emotion: {top_emotion['label']} ({top_emotion['score']:.2%} confidence)"

        return render_template('analysis.html', result=result, emotion_result=emotion_result)

    return render_template('analysis.html')

# auto logout
@app.route('/auto_logout', methods=['POST'])
@csrf.exempt
# @login_required
def auto_logout():
    logout_user()
    return '', 204