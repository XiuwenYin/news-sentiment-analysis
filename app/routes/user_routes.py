from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
import sqlalchemy as sa
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from sqlalchemy import func

from app.forms import FilterForm
from app.models import User, Post, db

user_bp = Blueprint("user", __name__)

@user_bp.route("/user/<username>", methods=["GET", "POST"])
@login_required
def user_profile(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    show_personal_inputs = user.age is None or user.gender is None

    form = FilterForm()
    age_group = None
    gender_filter = None
    category_distribution = {}

    if request.method == "POST":
        submitted_age = request.form.get("age")
        submitted_gender = request.form.get("gender")

        if submitted_age and not user.age:
            user.age = int(submitted_age)
        if submitted_gender and not user.gender:
            user.gender = submitted_gender

        db.session.commit()

        gender_filter = request.form.get("gender_filter")
        age_group = request.form.get("age_group")

        if gender_filter:
            result = db.session.execute(
                sa.select(Post.category, func.count(Post.id))
                .join(User)
                .where(User.gender == gender_filter)
                .group_by(Post.category)
            )
            category_distribution = dict(result.all())

        elif age_group:
            try:
                min_age, max_age = map(int, age_group.split("-"))
                result = db.session.execute(
                    sa.select(Post.category, func.count(Post.id))
                    .join(User)
                    .where(User.age.between(min_age, max_age))
                    .group_by(Post.category)
                )
                category_distribution = dict(result.all())
            except ValueError:
                flash("Invalid age group format", "danger")

    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    posts = Post.query.filter(
        Post.user_id == current_user.id,
        Post.timestamp >= seven_days_ago
    ).all()

    user_category_counter = Counter(post.category for post in posts if post.category)
    user_category_labels = list(user_category_counter.keys())
    user_category_values = list(user_category_counter.values())

    label_counts = {
        'Negative': sum(1 for post in posts if post.sentiment == 'Negative'),
        'Neutral': sum(1 for post in posts if post.sentiment == 'Neutral'),
        'Positive': sum(1 for post in posts if post.sentiment == 'Positive')
    }

    daily_sentiment = {}
    sentiment_counter = Counter()
    daily_post_count = Counter()

    for post in posts:
        date_str = post.timestamp.strftime('%Y-%m-%d')
        daily_post_count[date_str] += 1
        sentiment_counter[post.sentiment] += 1
        if date_str not in daily_sentiment:
            daily_sentiment[date_str] = Counter()
        daily_sentiment[date_str][post.sentiment] += 1

    dates = sorted(daily_sentiment.keys())
    positive = [daily_sentiment[d].get('Positive', 0) for d in dates]
    neutral = [daily_sentiment[d].get('Neutral', 0) for d in dates]
    negative = [daily_sentiment[d].get('Negative', 0) for d in dates]
    post_counts = [daily_post_count[d] for d in dates]

    return render_template(
        "user.html",
        user=user,
        form=form,
        posts=posts,
        age_group=age_group,
        gender_filter=gender_filter,
        label_counts=label_counts,
        dates=dates,
        positive=positive,
        neutral=neutral,
        negative=negative,
        post_counts=post_counts,
        sentiment_counter=sentiment_counter,
        category_distribution=category_distribution,
        category_labels=list(category_distribution.keys()) if category_distribution else [],
        category_values=list(category_distribution.values()) if category_distribution else [],
        show_personal_inputs=show_personal_inputs,
        user_category_labels=user_category_labels,
        user_category_values=user_category_values
    )
