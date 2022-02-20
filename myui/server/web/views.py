from flask import Blueprint, current_app, render_template
from mydataclasses.servers import Server

views = Blueprint('views', __name__)


@views.route("/")
def hello_world():
    server: Server = current_app.config["context"]
    return render_template('test.html', resources=server.resources)
