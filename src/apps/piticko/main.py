from flask import Blueprint, jsonify, request

piticko = Blueprint("bar", __name__)


# Order items in the store
@piticko.route("/order", methods=["POST"])
def order():
    data = request.get_json()


@piticko.route("/test", methods=["GET"])
def test():
    return jsonify({"message": "Hello, World!"})


# Some other endpoints here
