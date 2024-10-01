import uuid, json

from flask import Blueprint, jsonify, request
from flask_cors import cross_origin


market = Blueprint("market", __name__)


class Card:
    def __init__(self, name: str, desc: str, owner: str, img: str):
        self.name = name
        self.desc = desc
        self.owner = owner
        self.img = img

        self.id = str(uuid.uuid4())
        self.price = 0
        self.for_sale = False

        self.watchers = [] # list of users that are watching this card
    
    def __str__(self) -> str:
        return json.dumps(self.as_json())
    
    def as_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "desc": self.desc,
            "owner": self.owner,
            "img": self.img,
            "price": self.price,
            "for_sale": self.for_sale,
            "watchers": self.watchers
        }


EXISTING_CARDS: list[Card] = []


@market.route("/set_offer", methods=["POST"])
@cross_origin()
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
    
    # TODO: here notify watchers of this card that something happened
    
    return jsonify({"success": True}), 200

@market.route("/my_collection", methods=["POST"])
@cross_origin()
def my_collection():
    data: dict = request.get_json()

    user = data.get("user", None)

    if user is None:
        return jsonify({"error": "user not supplied"}), 400
    
    return jsonify({
        "success": True, "cards": [card.as_json() for card in EXISTING_CARDS if card.owner == user]
    }), 200

@market.route("/buy_card", methods=["POST"])
@cross_origin()
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

    # TODO: here notify watchers of this card that something happened

    return jsonify({"success": True}), 200

@market.route("/list_offers", methods=["POST"])
@cross_origin()
def list_offers():
    data: dict = request.get_json()

    user = data.get("user", None)

    if user is None:
        return jsonify({"error": "user not supplied"}), 400

    return jsonify({
        "success": True, "offers": [card.as_json() for card in EXISTING_CARDS if card.for_sale and card.owner != user]
    }), 200

@market.route("/set_watch", methods=["POST"])
@cross_origin()
def set_watch():
    data: dict = request.get_json()

    user = data.get("user", None)
    id = data.get("id", None)
    watch = data.get("watch", None)

    if user is None:
        return jsonify({"error": "user not supplied"}), 400
    if id is None:
        return jsonify({"error": "id not supplied"}), 400
    if watch is None:
        return jsonify({"error": "watch not supplied"}), 400

    card = None

    for x in EXISTING_CARDS:
        if x.id == id and x.owner != user:
            card = x
            break
    
    if card is None:
        return jsonify({"error": f"card with id {id} not found"}), 400

    if watch == True and user not in card.watchers:
        card.watchers.append(user)
    elif watch == False and user in card.watchers:
        card.watchers.remove(user)

    return jsonify({"success": True}), 200

# ADMIN

@market.route("/create_card", methods=["POST"])
@cross_origin()
def create_card():
    data: dict = request.get_json()

    name = data.get("name", None)
    owner = data.get("owner", None)
    desc = data.get("desc", None)
    img = data.get("img", None)

    if name is None:
        return jsonify({"error": "name not supplied"}), 400
    if owner is None:
        return jsonify({"error": "owner not supplied"}), 400
    if desc is None:
        return jsonify({"error": "desc not supplied"}), 400
    if img is None:
        return jsonify({"error": "img not supplied"}), 400

    card = Card(name, desc, owner, img)

    EXISTING_CARDS.append(card)

    return jsonify({"success": True, "id": card.id}), 200