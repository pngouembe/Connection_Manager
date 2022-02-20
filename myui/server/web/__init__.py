from flask import Flask
from mydataclasses.servers import Server

from .views import views

app = Flask(__name__)


def configure_app(server_config: Server):
    app.config['context'] = server_config

    app.register_blueprint(views, url_prefix='/')
    return app
