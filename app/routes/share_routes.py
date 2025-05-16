from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import sqlalchemy as sa

from app.models import Post, User, db, post_shares, Notification
from app.forms import SharePostForm
from transformers import pipeline

share_bp = Blueprint("share", __name__)

# Emotional Model
emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=None)

@share_bp.route("/share")
@login_required
def share():
    shared_posts = db.session.scalars(
        sa.select(Post)
        .join(post_shares)
        .where(post_shares.c.user_id == current_user.id)
    ).all()

    enriched_posts = []
    for post in shared_posts:
        emotion_scores = emotion_classifier(post.body, truncation=True, max_length=512)[0]
        sorted_emotions = sorted(emotion_scores, key=lambda x: x["score"], reverse=True)

        enriched_posts.append({
            "post": post,
            "emotions": sorted_emotions,
            "sentiment": post.sentiment,
            "category": post.category,
        })

    user_posts = Post.query.filter_by(user_id=current_user.id).all()
    other_users = User.query.filter(User.id != current_user.id).all()
    form = SharePostForm()

    return render_template(
        "share.html",
        enriched_posts=enriched_posts,
        user_posts=user_posts,
        other_users=other_users,
        form=form,
    )


@share_bp.route("/share_post/<int:post_id>", methods=["GET", "POST"])
@login_required
def share_post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == "POST":
        usernames = request.form.getlist("usernames")
        for username in usernames:
            user = User.query.filter_by(username=username).first()
            if user and user not in post.shared_with:
                post.shared_with.append(user)
        db.session.commit()
        flash("Post shared successfully!", "success")
        return redirect(url_for("share.share"))

    users = User.query.filter(User.id != current_user.id).all()
    return render_template("share_post.html", post=post, users=users)


@share_bp.route("/share_post_modal", methods=["POST"])
@login_required
def share_post_modal():
    post_id = request.form.get("post_id")
    user_id = request.form.get("user_id")

    post = Post.query.get_or_404(post_id)
    user = User.query.get_or_404(user_id)

    existing_share = db.session.execute(
        sa.select(post_shares).where(
            post_shares.c.post_id == post.id,
            post_shares.c.user_id == user.id
        )
    ).first()

    if not existing_share:
        db.session.execute(
            post_shares.insert().values(post_id=post.id, user_id=user.id)
        )
        notif = Notification(
            user_id=user.id,
            message=f'You have been shared a post: "{post.title}" by {current_user.username}'
        )
        db.session.add(notif)
        notif2 = Notification(
            user_id=current_user.id,
            message=f'You shared your post "{post.title}" with {user.username}'
        )
        db.session.add(notif2)
        db.session.commit()
        flash(f'Post "{post.title}" shared with {user.username}!', "success")
    else:
        flash(f'Post "{post.title}" is already shared with {user.username}.', "info")

    return redirect(url_for("share.share"))

@share_bp.route("/post/<int:post_id>")
@login_required
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("analysis.html", content=post.body)