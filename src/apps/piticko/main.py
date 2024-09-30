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
    if "items" not in request.json:
        return jsonify({"success": False, "error": "items is required"}), 400

    items: list[str] = request.json["items"]

    for item in items:
        if item in ALLOWED_ITEMS:
            continue

        return jsonify({"success": False, "error": f"{item} is not allowed"}), 400

    order: Order = Order(items)

    ORDERS.append(order)

    # Return only the secret id
    return jsonify({"secret_id": order.secret_id, "success": True})


# ADMIN


@piticko.route("/finish_order", methods=["POST"])
def finish_order():
    data = request.get_json()

    id = data["id"]

    order = None

    for existing_order in ORDERS:
        if existing_order.id == id:
            order = existing_order
            break
    
    if order is None:
        return jsonify({"error": f"Order with id {id} not found"}), 400

    order.finished = True

    return jsonify({"success": True}), 200