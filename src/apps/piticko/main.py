import uuid

from flask import Blueprint, jsonify, request

piticko = Blueprint("bar", __name__)

ORDERS = []  # Will be a database later?
ALLOWED_ITEMS = ["pizza", "beer", "burger"]


class Order:
    def __init__(self, items):
        self.id = str(uuid.uuid4())
        self.secret_id = str(uuid.uuid4())
        self.items = items
        self.finished = False

    def dict(self):
        return {
            "id": self.id,
            "secret_id": self.secret_id,
            "finished": self.finished,
            "items": self.items,
        }


@piticko.route("/create_order", methods=["POST"])
def create_order():
    order = request.json

    if "items" not in order:
        return jsonify({"error": "items is required"}), 400

    for item in order["items"]:
        if item not in ALLOWED_ITEMS:
            return jsonify({"error": f"{item} is not allowed"}), 400

    order = Order(order["items"])

    ORDERS.append(order)

    # Return only the secret id
    return jsonify({"secret_id": order.secret_id, "success": True})


# ADMIN


@piticko.route("/finish_order", methods=["POST"])
def finish_order():
    data = request.get_json()

    id = data["id"]

    