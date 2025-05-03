from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa

from app.models import User, Post, db
from flask import render_template, flash, redirect, url_for, request

from app import app, db
from app.forms import LoginForm, RegistrationForm
from urllib.parse import urlsplit
from transformers import (
    AutoTokenizer, 
    AutoModelForTokenClassification, 
    TokenClassificationPipeline,
    pipeline,
)
from transformers.pipelines import AggregationStrategy

import requests
from flask_login import login_required
import numpy as np
import feedparser

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



@app.route("/share", methods=["GET"])
@login_required
def share():
    ticker = "META"
    keyword = "meta"

    rss_url = f"https://www.news.com.au/content-feeds/latest-news-finance/"
    # Parse the RSS feed
    feed = feedparser.parse(rss_url)
    
    # Initialize the sentiment analysis pipeline
    classifier = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")
    label_map = {
        "LABEL_0": "Negative",
        "LABEL_1": "Neutral",
        "LABEL_2": "Positive"
    }
    
    # Perform sentiment analysis on each entry
    analyzed_entries = [0,0,0]
    for entry in feed.entries:
        summary = entry.title
        sentiment_result = classifier(summary)[0]
        # sentiment = label_map[sentiment_result["label"]]
        #
        # analyzed_entries.append({
        #     "title": title,
        #     "sentiment": sentiment,
        #     "confidence": f"{confidence:.2%}"
        # })
        # Increment the corresponding counter in the data list
        if sentiment_result["label"] == "LABEL_0":
            analyzed_entries[0] += 1
        if sentiment_result["label"] == "LABEL_1":
            analyzed_entries[1] += 1
        if sentiment_result["label"] == "LABEL_2":
            analyzed_entries[2] += 1
    
    # Pass the analyzed entries to the template
    return render_template("share.html", counter=analyzed_entries)

@app.route('/analysis', methods=['GET', 'POST'])
def analysis():
    label_map = {
        "LABEL_0": "Negative",
        "LABEL_1": "Neutral",
        "LABEL_2": "Positive"
    }

    result = None
    if request.method == 'POST':
        text_input = request.form.get('textInput', '')

        # Perform sentiment analysis or other processing here
        classifier = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")
        output = classifier(text_input)

        output_dict = output[0]  # <- this is a dict inside a list
        sentiment = label_map[output_dict["label"]]
        confidence = output_dict["score"]
        result = f"Sentiment: {sentiment} ({confidence:.2%} confidence)"

        # Keywords Extraction

        # Define keyphrase extraction pipeline
        class KeyphraseExtractionPipeline(TokenClassificationPipeline):
            def __init__(self, model, *args, **kwargs):
                super().__init__(
                    model=AutoModelForTokenClassification.from_pretrained(model),
                    tokenizer=AutoTokenizer.from_pretrained(model),
                    *args,
                    **kwargs
                )

            def postprocess(self, all_outputs):
                results = super().postprocess(
                    all_outputs=all_outputs,
                    aggregation_strategy=AggregationStrategy.FIRST,
                )
                return np.unique([result.get("word").strip() for result in results])
        
        # Load pipeline
        model_keywords = "ml6team/keyphrase-extraction-distilbert-inspec"
        extractor = KeyphraseExtractionPipeline(model=model_keywords)

        # Extract keywords and analyze sentiment of every keyword
        keywords = extractor(text_input)
        keywords_sentiment = []
        data = [0, 0, 0]
        for keyword in keywords:
            keyword_sentiment = classifier(keyword)
            keyword_sentiment_dict = keyword_sentiment[0]
            # sentiment = label_map[keyword_sentiment_dict["label"]]
            # confidence = keyword_sentiment_dict["score"]
            # keywords_sentiment.append(f"Keyword: {keyword}, Sentiment: {sentiment} ({confidence:.2%} confidence)")

            # Increment the corresponding counter in the data list
            if keyword_sentiment_dict["label"] == "LABEL_0":
                data[0] += 1
            if keyword_sentiment_dict["label"] == "LABEL_1":
                data[1] += 1
            if keyword_sentiment_dict["label"] == "LABEL_2":
                data[2] += 1

        # result = f"Processed text: {text_input}"  # Example result
        return render_template('analysis.html', result=result, counter=data)
    return render_template('analysis.html')


@app.route('/visualization', methods=['GET'])
def visualization():
    return render_template("visualization.html")

