import uuid

from flask import Blueprint, jsonify, request
from flask_cors import cross_origin

piticko = Blueprint("bar", __name__)


class Order:
    def __init__(self, items, user):
        self.id = len(ORDERS) + 1
        self.secret_id = str(uuid.uuid4())
        self.items = items
        self.user = user
        self.finished = False

    def dict(self):
        return {
            "id": self.id,
            "secret_id": self.secret_id,
            "finished": self.finished,
            "items": self.items,
            "user": self.user,
        }

    def dict_no_secret(self):
        return {
            "id": self.id,
            "finished": self.finished,
            "items": self.items,
            "user": self.user,
        }


ORDERS: list[Order] = []  # Will be a database later?
ITEMS = {
    "currency": "CZK",
    "currencySymbol": "Kč",
    "drinks": [
        {"name": "Voda 0.5l", "icon": "", "price": 20},
        {"name": "Coca Cola 0.5l", "icon": "", "price": 30},
        {"name": "Gin Tonic", "icon": "", "price": 145},
        {"name": "Skinny Bitch", "icon": "", "price": 135},
        {"name": "Coba Libre", "icon": "", "price": 145},
    ],
}


def find_item(name: str) -> int:
    for i, item in enumerate(ITEMS["drinks"]):
        if item["name"] == name:
            return i

    raise ValueError(f"Couldn't find item that satisfies query name='{name}")


@piticko.route("/create_order", methods=["POST"])
@cross_origin()
def create_order():
    if "order" not in request.json:
        return jsonify({"success": False, "error": "'order' is required"}), 400
    if "user" not in request.json:
        return jsonify({"success": False, "error": "'user' is required"}), 400

    items = request.json["order"]

    for item in items:
        if "name" not in item:
            return jsonify({"success": False, "error": "'name' is required"}), 400
        if "quantity" not in item:
            return jsonify({"success": False, "error": "'quantity' is required"}), 400

        try:
            find_item(item.get("name"))
        except ValueError:
            return (
                jsonify({"success": False, "error": f"{item.get('name')} not found"}),
                404,
            )

    user = request.json["user"]

    if len(user) == 0 or len(user) > 30:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "User name must be between 1 and 30 characters",
                }
            ),
            400,
        )
    if len(items) == 0:
        return (
            jsonify(
                {"success": False, "error": "Order must contain at least one item"}
            ),
            400,
        )

    order: Order = Order(items, user)

    ORDERS.append(order)

    return jsonify({"secret_id": order.secret_id, "id": order.id, "success": True})


@piticko.route("/get_items", methods=["GET"])
@cross_origin()
def get_items():
    return jsonify(ITEMS), 200


@piticko.route("/get_order_status", methods=["GET"])
@cross_origin()
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
@cross_origin()
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
@cross_origin()
def list_orders():
    return (
        jsonify(
            {"success": True, "orders": [order.dict_no_secret() for order in ORDERS]}
        ),
        200,
    )


@piticko.route("/pickup_order", methods=["POST"])
@cross_origin()
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
