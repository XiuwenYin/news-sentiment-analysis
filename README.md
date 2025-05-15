# 📰 News Sentiment Analysis Web Application

This is a web-based application that allows users to upload news articles or other text content and receive automated sentiment and emotion analysis. The application classifies each submission as **positive**, **negative**, or **neutral**, and also identifies detailed emotions such as **anger**, **disgust**, **fear**, **joy**, **sadness**, **surprise**, and **neutral**.

## 🚀 Features

- 📝 **Upload News or Articles**: Users can submit news articles through the web interface.
- 🤖 **Sentiment Classification**: Automatically analyze the text and label it as positive, negative, or neutral.
- 🎭 **Emotion Detection**: Detect multiple emotions expressed in the article including:
  - Anger
  - Disgust
  - Fear
  - Joy
  - Neutral
  - Sadness
  - Surprise
- 📜 **History Tracking**: Every article a user uploads is saved in their personal history for future reference.
- 🔗 **Share News**: Users can share their uploaded articles with others.

## 💡 Use Case

This tool can help:
- Journalists and media organizations track emotional tone in news reporting.
- Researchers analyze media sentiment trends.
- Readers assess emotional bias in news content.

## 🛠️ Tech Stack

- **Frontend**: HTML, CSS, JavaScript, Bootstrap/Semantic UI
- **Backend**: Flask (Python)
- **NLP Model**: Pre-trained transformer models (e.g., BERT, RoBERTa) via Hugging Face Transformers
- **Database**: SQLite (or other SQL-based DBMS)
- **APIs**: Flask RESTful API for sentiment/emotion analysis and history management

## 📦 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/news-sentiment-analysis.git
   cd news-sentiment-analysis


NLP models needs pytorch and transformers libraries.
```console
$ pip install transformers
```
```console
$ pip3 install torch torchvision
```
# news-sentiment-analysis

## Dev Env Setup
### Create virtual env
```console
$ python3 -m venv venv
```
### Activate virtual env
```console
$ source venv/bin/activate
```
### Install dependencies
```console
$ pip install -r requirements.txt
```

### Setting the FLASK_APP environment variable
```console
$ export FLASK_APP=news-sentiment-analysis.py
```

### Run the app
```console
$ flask run
```
