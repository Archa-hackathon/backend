#!/usr/bin/python3

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from apps.filter.main import filtr
from apps.piticko.main import piticko

app = Flask(__name__)
app.register_blueprint(piticko, url_prefix="/bar")
app.register_blueprint(filtr, url_prefix="/filter")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


if __name__ == "__main__":
    print(app.url_map)
    app.run(host="0.0.0.0", port=8080)
