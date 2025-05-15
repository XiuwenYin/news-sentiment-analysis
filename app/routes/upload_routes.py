from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
import sqlalchemy as sa
import re
from transformers import pipeline
from ..models import Post, db
from ..forms import UploadForm

upload_bp = Blueprint("upload", __name__)

# Classifiers
sentiment_classifier = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")
sentiment_label_map = {
    "LABEL_0": "Negative",
    "LABEL_1": "Neutral",
    "LABEL_2": "Positive"
}
emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=None)
news_category_classifier = pipeline("text-classification", model="joeddav/distilbert-base-uncased-agnews-student", top_k=1)
news_summarizer = pipeline("summarization", model="t5-small")


@upload_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if not current_user.is_authenticated:
        flash("You need to log in to upload news content.", "warning")
        return redirect(url_for("main.index"))

    form = UploadForm()
    if form.validate_on_submit():
        post_title = form.post_title.data
        news_content = form.news_content.data.replace("\r\n", "\n").replace("\r", "\n")

        # Predict category
        result = news_category_classifier(news_content, truncation=True, max_length=512)
        category_result = result[0][0]['label']

        # Count characters and sentences
        char_count = len(news_content)
        sentence_count = len([s for s in re.split(r"[.!?]", news_content) if s.strip()])

        # Generate summary
        summary_output = news_summarizer(news_content, max_length=130, min_length=30, do_sample=False)
        summary_text = summary_output[0]["summary_text"]

        # Emotion analysis
        emotion_scores = emotion_classifier(news_content, truncation=True, max_length=512)[0]
        emotion_scores_sorted = sorted(emotion_scores, key=lambda x: x["score"], reverse=True)

        # Sentiment
        sentiment_output = sentiment_classifier(news_content, truncation=True, max_length=512)
        sentiment = sentiment_label_map[sentiment_output[0]["label"]]

        # Save to DB
        post = Post(title=post_title, body=news_content, author=current_user)
        post.sentiment = sentiment
        post.category = category_result
        post.emotions = {e["label"]: round(e["score"], 3) for e in emotion_scores_sorted}
        db.session.add(post)
        db.session.commit()

        return render_template(
            "visualize.html",
            content=news_content,
            result=sentiment,
            char_count=char_count,
            sentence_count=sentence_count,
            emotion_scores=emotion_scores_sorted,
            news_category=category_result,
            summary=summary_text,
        )

    return render_template("upload.html", form=form)
