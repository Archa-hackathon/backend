from flask import Blueprint, jsonify, request


filtr = Blueprint("filter", __name__)


@filtr.route("/question", methods=["POST"])
def question():
    pass