import sqlite3
import ollama
import json, os

from flask import Blueprint, current_app, g, jsonify, request, Response
from flask import copy_current_request_context

from .goout_event_list import UPCOMING_EVENTS_PROPMT


chatbot = Blueprint("chatbot", __name__)


ollama_client = ollama.Client("http://192.168.0.101:1111")
with open(os.path.join(os.path.dirname(__file__), "system_prompt.json"), "r") as file:
    SYSTEM_PROMPT = json.load(file)


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


@chatbot.route("/question", methods=["POST"])
def question():
    data: dict = request.get_json()

    question = data.get("question", None)

    if question is None:
        return jsonify({"error": "No question provided."}), 400
    
    try:
        response = ollama_client.chat(
            model="llama3.2",
            messages=SYSTEM_PROMPT + UPCOMING_EVENTS_PROPMT + [
                {
                    "role": "user",
                    "content": question
                }
            ]
        )

        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chatbot.route("/question_stream", methods=["POST"])
def question_stream():
    data: dict = request.get_json()

    question = data.get("question", None)

    if question is None:
        return jsonify({"error": "No question provided."}), 400

    try:
        response = ollama_client.chat(
            stream=True,
            model="llama3.2",
            messages=SYSTEM_PROMPT + UPCOMING_EVENTS_PROPMT + [
                {
                    "role": "user",
                    "content": question
                }
            ]
        )

        @copy_current_request_context
        def generator():
            for chunk in response:
                yield f"{json.dumps(chunk)}\n"

        return Response(generator(), content_type="text/plain")
    except Exception as e:
        return jsonify({"error": str(e)}), 500