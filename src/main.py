#!/usr/bin/python3

from flask import Flask
from flask_migrate import Migrate

from extensions import db


def create_app():
    app = Flask(__name__)

    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize the database with the app
    db.init_app(app)

    # Initialize Flask-Migrate
    Migrate(app, db)

    # Register the blueprints
    #from apps.filter.main import filtr
    from apps.piticko.main import piticko
    from apps.chatbot.main import chatbot

    app.register_blueprint(piticko, url_prefix="/bar")
    #app.register_blueprint(filtr, url_prefix="/filter")
    app.register_blueprint(chatbot, url_prefix="/chatbot")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8080)
