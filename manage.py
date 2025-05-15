from app import create_app, db
from app.models import User, Post, Notification
from flask_migrate import Migrate
from config import Config

app = create_app(Config)
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "User": User, "Post": Post, "Notification": Notification}


if __name__ == "__main__":
    app.run(debug=True)
