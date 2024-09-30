import uuid

from flask import Blueprint, jsonify, request

piticko = Blueprint("bar", __name__)


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

    def dict_no_secret(self):
        return {
            "id": self.id,
            "finished": self.finished,
            "items": self.items,
        }


ORDERS: list[Order] = []  # Will be a database later?
ALLOWED_ITEMS = ["pizza", "beer", "burger"]


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


@piticko.route("/get_order_status", methods=["GET"])
def get_order_status():
    secret_id: str | None = request.args.get("secret_id")

    if secret_id is None:
        return jsonify({"success": False, "error": "secret_id is required"}), 400

    for order in ORDERS:
        if order.secret_id != secret_id:
            continue

        return jsonify({"success": True, "finished": order.finished}), 200

    return jsonify({"success": False, "error": "Order not found"}), 404


# ADMIN


@piticko.route("/finish_order", methods=["POST"])
def finish_order():
    data = request.get_json()

    if "id" not in data:
        return jsonify({"error": "Supplied data does not contain an order id."}), 400

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


@piticko.route("/list_orders", methods=["GET"])
def list_orders():
    return (
        jsonify(
            {"success": True, "orders": [order.dict_no_secret() for order in ORDERS]}
        ),
        200,
    )


@piticko.route("/pickup_order", methods=["POST"])
def pickup_order():
    data = request.get_json()

    if "secret_id" not in data:
        return (
            jsonify({"error": "Supplied data does not contain an order secret_id."}),
            400,
        )

    secret_id = data["secret_id"]

    order = None

    for existing_order in ORDERS:
        if existing_order.secret_id == secret_id:
            order = existing_order
            break

    if order is None:
        return jsonify({"exists": False}), 200

    ORDERS.remove(order)

    return jsonify({"exists": True, "order": order.dict()}), 200

