import os

from flask import Flask
from config import Config

## Create and initialis the Flask application instance
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    with app.app_context():
        from . import routes
        app.register_blueprint(routes.bp)

    return app