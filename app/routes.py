from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa

from app.models import User, Post, db
from flask import render_template, flash, redirect, url_for, request

from app import app, db
from app.forms import LoginForm, RegistrationForm
from urllib.parse import urlsplit

from flask_login import login_required


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
    return render_template("login.html", title="Sign In", form=form)


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
    return render_template("register.html", title="Register", form=form)


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        news_content = request.form["news_content"]
        sentiment_result = "Positive"  # 占位

        # 保存到Post并提交
        post = Post(body=news_content, author=current_user)
        db.session.add(post)
        db.session.commit()

        return render_template("visualize.html", content=news_content, result=sentiment_result)

    return render_template("upload.html", title="Upload News")


@app.route("/share")
@login_required
def share():
    return render_template("share.html")

