from flask import Flask
from users import User, UserInfo
from .views import views

app = Flask(__name__)


def configure_app(client_config: User):
    app.config['context'] = client_config

    app.register_blueprint(views, url_prefix='/')
    return app
