from flask import Blueprint, current_app, render_template
from users import User
views = Blueprint('views', __name__)


@views.route("/")
def dashboard():
    user: User = current_app.config["context"]
    return render_template('dashboard.html')
