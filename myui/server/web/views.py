from flask import Blueprint, current_app, render_template
from mydataclasses.servers import Server

views = Blueprint('views', __name__)


@views.route("/")
def dashboard():
    server: Server = current_app.config["context"]
    return render_template('dashboard.html', resources=server.resources)
