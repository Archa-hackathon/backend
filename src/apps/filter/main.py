import sqlite3

from flask import Blueprint, current_app, g, jsonify, request

filtr = Blueprint("filter", __name__)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


@filtr.route("/question", methods=["POST"])
def question():
    pass
