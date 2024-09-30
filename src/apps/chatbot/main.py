import ollama
import json, os
from uuid import uuid4

from flask import Blueprint, jsonify, request, Response
from flask import copy_current_request_context

from .goout_event_list import UPCOMING_EVENTS_PROPMT


chatbot = Blueprint("chatbot", __name__)

class Chat:
    def __init__(self, model: str):
        self.id = str(uuid4())
        self.model = model

        with open(os.path.join(os.path.dirname(__file__), "system_prompt.json"), "r") as file:
            sys_prompt = json.load(file)

        self.messages = [{
            "role": "system",
            "content": sys_prompt
        }]
    
    def question(self, prompt):
        pass

CHATS = []

ollama_client = ollama.Client("http://192.168.0.101:1111")


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