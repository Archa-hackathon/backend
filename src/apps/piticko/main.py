from flask import Blueprint, jsonify, request

piticko = Blueprint("bar", __name__)

ORDERS = []  # Will be a database later?
ALLOWED_ITEMS = ["pizza", "beer", "burger"]


@piticko.route("/create_order", methods=["POST"])
def create_order():
    order = request.json

    if not "items" in order:
        return jsonify({"error": "items is required"}), 400

    for item in order["items"]:
        if item not in ALLOWED_ITEMS:
            return jsonify({"error": f"{item} is not allowed"}), 400

    order_obj = {"id": 1}  # Calculate id later


# ADMIN


@piticko.route("/finish_order", methods=["POST"])
def finish_order():
    data = request.get_json()

    id = data["id"]

    