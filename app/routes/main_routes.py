# app/routes/main_routes.py
from flask import render_template
from flask_login import login_required
from flask import Blueprint

main = Blueprint("main", __name__)

@main.route("/")
@main.route("/index")
def index():
    return render_template("homepage.html")



