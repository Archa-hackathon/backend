import uuid, json

from flask import Blueprint, jsonify, request
from flask_cors import cross_origin


market = Blueprint("market", __name__)


class Card:
    def __init__(self, name: str, owner: str):
        self.id = str(uuid.uuid4())
        self.owner = owner
        self.name = name

        self.price = 0
        self.for_sale = False
    
    def __str__(self) -> str:
        return json.dumps({
            "id": self.id,
            "owner": self.owner,
            "name": self.name,
            "price": self.price
        })


EXISTING_CARDS: list[Card] = []


@market.route("/set_offer", methods=["POST"])
def set_offer():
    data: dict = request.get_json()

    user = data.get("user", None)
    id = data.get("id", None)
    price = data.get("price", None)

    if user is None:
        return jsonify({"error": "user not supplied"}), 400
    if id is None:
        return jsonify({"error": "id not supplied"}), 400
    if price is None:
        return jsonify({"error": "price not supplied"}), 400

    card: Card = None

    for x in EXISTING_CARDS:
        if x.id == id and x.owner == user:
            card = x
            break
    
    if card is None:
        return jsonify({"error": f"card with id {id} not owned by user {user}"}), 400
    
    if price == 0:
        card.for_sale = False
    else:
        card.price = price
        card.for_sale = True
    
    return jsonify({"success": True}), 200

@market.route("/buy_card", methods=["GET"])
def buy_card():
    data: dict = request.get_json()

    user = data.get("user", None)
    id = data.get("id", None)

    if user is None:
        return jsonify({"error": "user not supplied"}), 400
    if id is None:
        return jsonify({"error": "id not supplied"}), 400

    card: Card = None

    for x in EXISTING_CARDS:
        if x.id == id and x.for_sale and x.owner != user:
            card = x
            break
    
    if card is None:
        return jsonify({"error": f"no valid offer found"}), 400
    
    card.owner = user
    card.for_sale = False

    return jsonify({"success": True}), 200

@market.route("/list_offers", methods=["GET"])
def list_offers():
    return jsonify({
        "success": True, "offers": [str(card) for card in EXISTING_CARDS if card.for_sale]
    }), 200

# ADMIN

@market.route("/create_card", methods=["POST"])
def create_card():
    data: dict = request.get_json()

    name = data.get("name", None)
    owner = data.get("owner", None)

    if name is None:
        return jsonify({"error": "name not supplied"}), 400
    if owner is None:
        return jsonify({"error": "owner not supplied"}), 400

    card = Card(name, owner)

    EXISTING_CARDS.append(card)