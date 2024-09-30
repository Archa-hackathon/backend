import ollama
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin

SYSTEM_PROMPT = [
    {
        "role": "system",
        "content": "Jsi AI chatbot, který generuje otázky na zadané téma. Pracuješ v aplikaci pro divadlo ARCHA.",
    },
]

otazky = Blueprint("otazky", __name__)
ollama_client = ollama.Client("http://192.168.0.101:1111")


# ADMIN
@otazky.route("/generate_question", methods=["POST"])
@cross_origin()
def generate_question():
    data = request.get_json()

    if "topic" not in data:
        return jsonify({"error": "Supplied data does not contain a topic."}), 400

    response_data = ollama_client.chat(
        model="llama3.2",
        messages=SYSTEM_PROMPT
        + [{"role": "user", "content": f"Téma: {data['topic']}"}],
    )

    response: str = response_data["message"]["content"]

    return jsonify(response), 200
