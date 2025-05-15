from flask import Blueprint, render_template
from flask_login import login_required, current_user
from collections import defaultdict
from app.models import Post

history_bp = Blueprint("history", __name__)

@history_bp.route("/history")
@login_required
def history():
    posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.timestamp.desc()).all()
    grouped_posts = defaultdict(list)
    for post in posts:
        date_str = post.timestamp.strftime("%Y-%m-%d")
        grouped_posts[date_str].append(post)
    return render_template("history.html", grouped_posts=grouped_posts)


@history_bp.route("/post/<int:post_id>")
@login_required
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("analysis.html", content=post.body)
