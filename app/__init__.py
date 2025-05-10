from flask import Flask, url_for
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf import CSRFProtect  # CSRF protection


app = Flask(__name__)

app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

csrf = CSRFProtect()  # Instantiate
csrf.init_app(app)   # Bind to Flask app instance

if __name__ == "__main__":
    app.run(debug=True)

from app import routes, models