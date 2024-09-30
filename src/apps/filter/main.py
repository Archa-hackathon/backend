import sqlite3
import ollama

from flask import Blueprint, current_app, g, jsonify, request

filtr = Blueprint("filter", __name__)


ollama_client = ollama.Client("http://192.168.0.101:1111")


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
    data: dict = request.get_json()

    question = data.get("question", None)

    if question is None:
        return jsonify({"error": "No question provided."}), 400
    
    try:
        response = ollama_client.chat(
            model="llama3.2",
            messages=[
                {
                    "role": "user",
                    "content": question
                }
            ]
        )

        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
