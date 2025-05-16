# 📰 News Sentiment Analysis Web Application

This is a web-based application that allows users to upload news articles or other text content and receive automated sentiment and emotion analysis. The application classifies each submission as **positive**, **negative**, or **neutral**, and also identifies detailed emotions such as **anger**, **disgust**, **fear**, **joy**, **sadness**, **surprise**, and **neutral**.

---

## 👥 Contributors

| UWA ID    | Name         | GitHub Username  |
|-----------|--------------|------------------|
| 24332945  | Xiuwen Yin   | XiuwenYin        |
| 24305445  | Yanxi Liu    | yanxiliu33       |
| 24103755  | Simon Liu    | Zhuzilinaba      |
| 23884492  | Zihan Wu     | ZihanWu2025      |

Repository: [https://github.com/XiuwenYin/news-sentiment-analysis](https://github.com/XiuwenYin/news-sentiment-analysis)

---

## 🚀 Features

- 📝 **Upload News or Articles**: Users can submit news articles through the web interface.
- 🤖 **Sentiment Classification**: Automatically analyze the text and label it as positive, negative, or neutral.
- 🎭 **Emotion Detection**: Detect multiple emotions expressed in the article including:
  - Anger
  - Disgust
  - Fear
  - Joy
  - Sadness
  - Surprise
  - Neutral
- 📊 **Data Visualization**: Users can view their recent post sentiments and category distributions.
- 📜 **History Tracking**: Every article a user uploads is saved in their personal history for future reference.
- 🔗 **Share News**: Users can selectively share their analysis results with other registered users.

---

## 💡 Use Cases

This tool can help:
- Journalists and media organizations track emotional tone in reporting.
- Researchers analyze media sentiment trends across time.
- Readers assess emotional bias in content to make informed judgments.

---

## 🛠️ Tech Stack

| Layer     | Technologies                     |
|-----------|----------------------------------|
| Frontend  | HTML, CSS, JavaScript, Bootstrap |
| Backend   | Flask, Flask-Login, Flask-WTF    |
| NLP Model | HuggingFace Transformers (BERT)  |
| Database  | SQLite + SQLAlchemy ORM          |
| Testing   | Pytest, Flask-Testing            |

---

## 📦 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/XiuwenYin/news-sentiment-analysis.git
cd news-sentiment-analysis
```

### 2. Create and Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install NLP Model Dependencies
```bash
pip install transformers
pip install torch torchvision
```

### 5. Set Environment Variable
```bash
export FLASK_APP=app  # or use `set FLASK_APP=app` on Windows
```

### 6. Initialize the Database
```bash
flask db upgrade
```

### 7. Run the Application
```bash
flask run
```

Access via: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🧪 Running Tests

To run all unit tests:
```bash
pytest tests/
```

Our test suite covers:
- Upload form validation
- Route functionality (upload, history, insights, sharing)
- Sentiment model mocking
- Access control (authentication required)

---

## 📁 Project Structure

```
news-sentiment-analysis/
│
├── app/                    # Main application code
│   ├── models.py           # Database models
│   ├── forms.py            # WTForms definitions
│   ├── routes/             # Blueprinted routes
│   ├── templates/          # HTML templates
│   └── static/             # Static assets (CSS, JS, images)
│
├── tests/                  # Unit test suite
│
├── requirements.txt        # Python dependencies
├── config.py               # App configurations
├── run.py / app.py         # Flask app entry point
└── README.md               # Project description
```

---

## 🤝 Contribution

We welcome bug reports and suggestions. Please open issues or pull requests in the GitHub repository.