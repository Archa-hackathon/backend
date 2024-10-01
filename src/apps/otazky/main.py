import json
import os

import openai
import requests
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin

SYSTEM_PROMPT = [
    {
        "role": "system",
        "content": 'Jsi AI chatbot, který generuje otázky na zadané téma. Odpovídej VELMI stručně - otázka musí být jedna krátká věta! Formát musí být JSON: {"question": "příklad otázka", "answers": ["odpověď jedna", "odpoved dva", "odpoved tri"], "correct": 1}. Vždycky tři odpovědi, jedna správná (index). Pracuješ v aplikaci pro divadlo ARCHA.',
    },
]

KEY_ENV_NAME = "STUCKINVIM_KEY"
ROTATOR_URL = "http://getkey.stuckinvim.com/api/data?api_key=%key%"
MODEL = "gpt-4o-mini"

Questions = []


def fetch_key():
    # Get the value of KEY_ENV_NAME in .env
    stuckinvim_key = os.environ.get(KEY_ENV_NAME)

    assert (
        stuckinvim_key is not None
    ), f"Please set {KEY_ENV_NAME} in the .env to your key rotator key!"

    # Fetch the actual open ai key
    response = requests.get(ROTATOR_URL.replace("%key%", stuckinvim_key))

    assert response.status_code == 200, "Invalid key rotator key!"
    assert (
        response.json().get("key", None) is not None
    ), "Key rotator returned invalid response!"

    return response.json()["key"]


client = openai.Client(api_key=fetch_key())
otazky = Blueprint("otazky", __name__)


@otazky.route("/get_questions", methods=["GET"])
@cross_origin()
def get_questions():
    # Remove the correct answer from all questions
    sanitized_questions = [
        {"question": q.get("question"), "answers": q.get("answers")} for q in Questions
    ]

    return jsonify(sanitized_questions), 200


@otazky.route("/answer_question", methods=["POST"])
@cross_origin()
def answer_question():
    data = request.get_json()

    if "question" not in data:
        return jsonify({"error": "Supplied data does not contain a question."}), 400
    if "answer" not in data:
        return jsonify({"error": "Supplied data does not contain an answer."}), 400

    for q in Questions:
        if q.get("question") != data["question"]:
            continue

        is_correct = q.get("correct") == data["answer"]
        return jsonify({"correct": is_correct}), 200

    return jsonify({"error": "Question not found."}), 404


# ADMIN
@otazky.route("/generate_question", methods=["POST"])
@cross_origin()
def generate_question():
    data = request.get_json()

    if "topic" not in data:
        return jsonify({"error": "Supplied data does not contain a topic."}), 400

    chat_completion = client.chat.completions.create(
        messages=SYSTEM_PROMPT
        + [{"role": "user", "content": f"Téma: {data['topic']}"}],
        model=MODEL,
        temperature=0.1,
    )

    response: str = chat_completion.choices[0].message.content
    response_json = json.loads(response)

    Questions.append(response_json)

    return jsonify(response), 200
